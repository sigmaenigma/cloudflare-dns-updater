#!/usr/bin/env python3
import requests
import json
from datetime import datetime
import socket
import logging
import time

logging.basicConfig(level=logging.INFO)

class Config:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)

    def load_config(self, config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f'Error loading config file: {e}')
            raise

    def get(self, key):
        return self.config.get(key)

class CloudFlareUpdater:
    def __init__(self, config):
        self.config = config
        self.headers = self.get_headers()

    def get_headers(self):
        try:
            token = self.config.get('token')
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        except Exception as e:
            logging.error(f'Error getting headers: {e}')
            raise

    def verify_api(self):
        try:
            url = "https://api.cloudflare.com/client/v4/user/tokens/verify"
            response = requests.get(url=url, headers=self.headers)
            response.raise_for_status()
            return response.json().get('result', {}).get('status') == 'active'
        except Exception as e:
            logging.error(f'Error verifying API token: {e}')
            return False

    def get_current_public_ip(self):
        try:
            return requests.get('https://api.ipify.org').text
        except Exception as e:
            logging.error(f'Error getting current public IP: {e}')
            raise

    def get_zone_data(self):
        try:
            zone_name = self.config.get('zone_name')
            record_name = self.config.get('record_name')
            url = f"https://api.cloudflare.com/client/v4/zones/{zone_name}/dns_records?name={record_name}"
            response = requests.get(url=url, headers=self.headers)
            response.raise_for_status()
            return response.json().get('result', [])[0]
        except Exception as e:
            logging.error(f'Error getting zone data: {e}')
            raise

    def update_ip_in_cloudflare(self, current_public_ip, zone_data):
        try:
            cloudflare_ip = zone_data["content"]
            if current_public_ip != cloudflare_ip or self.config.get("force_update"):
                logging.info(f'Updating CloudFlare IP from {cloudflare_ip} to {current_public_ip}')
                url = f"https://api.cloudflare.com/client/v4/zones/{zone_data['zone_id']}/dns_records/{zone_data['id']}"
                payload = {
                    "content": current_public_ip,
                    "name": zone_data["name"],
                    "proxied": False,
                    "type": "A",
                    "comment": f"IP last updated on {datetime.now()} via API User from hostname {socket.gethostname()}",
                    "ttl": 3600
                }
                response = requests.patch(url=url, json=payload, headers=self.headers)
                response.raise_for_status()
                logging.info('IP successfully updated in CloudFlare')
            else:
                logging.info('IP addresses are the same. No update needed.')
        except Exception as e:
            logging.error(f'Error updating IP in CloudFlare: {e}')
            raise

def main():
    try:
        config = Config()
        updater = CloudFlareUpdater(config)
        interval_minutes = config.get('interval_minutes')
        while True:
            if updater.verify_api():
                current_public_ip = updater.get_current_public_ip()
                zone_data = updater.get_zone_data()
                updater.update_ip_in_cloudflare(current_public_ip, zone_data)
            else:
                logging.error('API token verification failed.')
            logging.info(f'Waiting for {interval_minutes} minutes before next update...')
            time.sleep(interval_minutes * 60)
    except Exception as e:
        logging.error(f'Error in main: {e}')

if __name__ == '__main__':
    main()
