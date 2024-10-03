#!/usr/bin/env python3
from app import Config, CloudFlareUpdater
import logging

__author__ = "Adrian Sanabria-Diaz"
__license__ = "MIT"
__version__ = "2.0.1"
__maintainer__ = "Adrian Sanabria-Diaz"
__status__ = "Production"

logging.basicConfig(level=logging.INFO)

def main():
    try:
        config = Config()
        updater = CloudFlareUpdater(config)
        if updater.verify_api():
            current_public_ip = updater.get_current_public_ip()
            zone_data = updater.get_zone_data()
            updater.update_ip_in_cloudflare(current_public_ip, zone_data)
        else:
            logging.error('API token verification failed.')
    except Exception as e:
        logging.error(f'Error in manual_app: {e}')

if __name__ == '__main__':
    main()
