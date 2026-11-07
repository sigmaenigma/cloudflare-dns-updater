#!/usr/bin/env python3
"""Run a single check-and-update cycle and exit. Exits non-zero on failure."""
import sys

from app import CloudFlareUpdater, Config, ConfigError, configure_logging, log

__author__ = "Adrian Sanabria-Diaz"
__license__ = "MIT"
__version__ = "3.0.0"
__maintainer__ = "Adrian Sanabria-Diaz"
__status__ = "Production"


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

    try:
        updater.run_once()
    except Exception as e:  # noqa: BLE001 - report any failure as a non-zero exit
        log.error("Update failed: %s", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
