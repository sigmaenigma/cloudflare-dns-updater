#!/usr/bin/env python3
"""Keep a Cloudflare A record pointed at this host's current public IPv4 address.

Run this file directly for a perpetual loop that checks on an interval, or run
app_manual.py for a single check that exits.
"""
import ipaddress
import json
import logging
import os
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

__author__ = "Adrian Sanabria-Diaz"
__license__ = "MIT"
__version__ = "3.0.0"
__maintainer__ = "Adrian Sanabria-Diaz"
__status__ = "Production"

CLOUDFLARE_API = "https://api.cloudflare.com/client/v4"
PUBLIC_IP_URL = "https://api.ipify.org"
REQUEST_TIMEOUT = 10  # seconds; requests has no default and would hang forever
COMMENT_MAX_LEN = 100  # Cloudflare's limit for DNS record comments
DEFAULT_INTERVAL_MINUTES = 15

log = logging.getLogger("cloudflare-dns-updater")


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


class ConfigError(Exception):
    """Raised when the config file is missing, unreadable, or incomplete."""


class Config:
    """Settings from config.json. CF_API_TOKEN in the environment overrides "token"."""

    def __init__(self, config_file=None):
        self.path = Path(
            config_file
            or os.environ.get("CONFIG_FILE")
            or Path(__file__).resolve().parent / "config.json"
        )
        data = self._read(self.path)
        self.token = os.environ.get("CF_API_TOKEN") or data.get("token")
        self.zone_id = data.get("zone_id")
        self.dns_record_name = data.get("dns_record_name")
        self.force_update = bool(data.get("force_update", False))
        self.interval_minutes = data.get("interval_minutes", DEFAULT_INTERVAL_MINUTES)
        self._validate()

    @staticmethod
    def _read(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise ConfigError(
                f"Config file not found: {path}. "
                "Copy config.example.json to config.json and fill it in."
            ) from None
        except OSError as e:
            raise ConfigError(f"Could not read config file {path}: {e}") from None
        except json.JSONDecodeError as e:
            raise ConfigError(f"Config file {path} is not valid JSON: {e}") from None
        if not isinstance(data, dict):
            raise ConfigError(f"Config file {path} must contain a JSON object")
        return data

    def _validate(self):
        problems = []
        if not isinstance(self.token, str) or not self.token.strip():
            problems.append(
                '"token" is required: set it in the config file '
                "or in the CF_API_TOKEN environment variable"
            )
        for name in ("zone_id", "dns_record_name"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                problems.append(f'"{name}" is required and must be a non-empty string')
        interval = self.interval_minutes
        if (
            isinstance(interval, bool)
            or not isinstance(interval, (int, float))
            or interval <= 0
        ):
            problems.append('"interval_minutes" must be a positive number')
        if problems:
            raise ConfigError("Invalid configuration: " + "; ".join(problems))


class CloudFlareUpdater:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {config.token}"

    def _cloudflare(self, method, path, **kwargs):
        """Call the Cloudflare API and return the parsed "result" field.

        Raises requests.HTTPError with Cloudflare's own error messages on failure.
        """
        response = self.session.request(
            method, f"{CLOUDFLARE_API}{path}", timeout=REQUEST_TIMEOUT, **kwargs
        )
        try:
            body = response.json()
        except ValueError:
            body = {}
        if not response.ok or not body.get("success", False):
            errors = "; ".join(
                f"{e.get('code')}: {e.get('message')}" for e in body.get("errors", [])
            )
            raise requests.HTTPError(
                f"Cloudflare API {method} {path} failed with HTTP "
                f"{response.status_code}: {errors or response.text[:200]}",
                response=response,
            )
        return body.get("result")

    def verify_token(self):
        """Return True if the configured token is valid and active."""
        try:
            result = self._cloudflare("GET", "/user/tokens/verify") or {}
        except requests.RequestException as e:
            log.error("Could not verify API token: %s", e)
            return False
        status = result.get("status")
        if status != "active":
            log.error("API token status is %r, expected 'active'", status)
            return False
        log.info("API token verified")
        return True

    def get_current_public_ip(self):
        response = requests.get(PUBLIC_IP_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        text = response.text.strip()
        try:
            return str(ipaddress.IPv4Address(text))
        except ipaddress.AddressValueError:
            raise ValueError(
                f"Public IP lookup did not return an IPv4 address: {text[:100]!r}"
            ) from None

    def get_dns_record(self):
        name = self.config.dns_record_name
        records = self._cloudflare(
            "GET",
            f"/zones/{self.config.zone_id}/dns_records",
            params={"name": name, "type": "A"},
        ) or []
        if not records:
            raise LookupError(
                f"No A record named {name!r} exists in zone {self.config.zone_id}. "
                "Create it in Cloudflare first; this script only updates records."
            )
        if len(records) > 1:
            log.warning("Found %d A records named %s; updating the first", len(records), name)
        return records[0]

    def update_dns_record(self, current_ip, record):
        """PATCH the record's content if it differs. Returns True if an update was sent.

        Only "content" and "comment" are sent, so proxied status and TTL are preserved.
        """
        if current_ip == record["content"] and not self.config.force_update:
            log.info("Cloudflare already has %s. No update needed.", current_ip)
            return False
        log.info("Updating %s from %s to %s", record["name"], record["content"], current_ip)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        comment = f"Updated {stamp} by cloudflare-dns-updater on {socket.gethostname()}"
        self._cloudflare(
            "PATCH",
            f"/zones/{self.config.zone_id}/dns_records/{record['id']}",
            json={"content": current_ip, "comment": comment[:COMMENT_MAX_LEN]},
        )
        log.info("Record updated successfully")
        return True

    def run_once(self):
        """One full check-and-update cycle. Raises on any failure."""
        current_ip = self.get_current_public_ip()
        record = self.get_dns_record()
        return self.update_dns_record(current_ip, record)


def main():
    configure_logging()
    try:
        config = Config()
    except ConfigError as e:
        log.error("%s", e)
        return 1

    updater = CloudFlareUpdater(config)
    if not updater.verify_token():
        return 1

    log.info(
        "Watching %s every %s minute(s)", config.dns_record_name, config.interval_minutes
    )
    try:
        while True:
            try:
                updater.run_once()
            except Exception as e:  # noqa: BLE001 - keep the daemon alive through transient failures
                log.error("Update cycle failed: %s", e)
            log.info("Next check in %s minute(s)", config.interval_minutes)
            time.sleep(config.interval_minutes * 60)
    except KeyboardInterrupt:
        log.info("Stopping")
    return 0


if __name__ == "__main__":
    sys.exit(main())
