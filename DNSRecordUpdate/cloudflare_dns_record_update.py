#!/usr/bin/env python3
import requests
import json
from datetime import datetime
import socket

__author__ = "Adrian Sanabria-Diaz"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Adrian Sanabria-Diaz"
__status__ = "Production"

""" 
Update your DNS record in CloudFlare with your Home IP  
"""

def get_hostname():
    try:
        return socket.gethostname()
    except Exception as e:
        print(f'An issue occurred trying to get the system hostname: {e}')
        return e

def get_config():
    """ Opens the JSON config file and returns the contents """
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(f'An issue occurred trying to open the configuration file: {e}')

def get_verify_api():
    """ Verifies the Token works and returns True if it does """
    try:
        url = f"https://api.cloudflare.com/client/v4/user/tokens/verify"
        headers = get_headers()
        response = requests.get(url=url, headers=headers)
        json_response = response.json()
        status = response.json()['result']['status']
        if "result" in json_response:
            return True if status == 'active' else False
        else:
            return False
    except Exception as e:
        print(f'An issue occurred with get_verify_api(): {e}')
        return False

def get_headers():
    """ Returns Headers with token """
    try:
        token = get_config()['token']
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        return headers
    except Exception as e:
        print(f'An issue occurred getting headers: {e}')
        return False

def update_ip_in_cloudflare(current_public_ip, zone_data):
    """ Updates the IP (content) in CloudFlare if a change is detected or the Force flag is enabled for a given domain name """
    try:
        config = get_config()
        hostname = get_hostname()
        cloudflare_ip = zone_data["content"]
        name          = zone_data["name"]
        id            = zone_data["id"]
        zone_id       = zone_data["zone_id"]
        force_update  = config["force_update"]
        if current_public_ip != cloudflare_ip or force_update == True:
            print(f'Updating the CloudFlare IP {cloudflare_ip} with the current public IP: {current_public_ip} from hostname: {hostname}')
            current_time = datetime.now()
            headers = get_headers()
            url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{id}"
            payload = {
                "content":  f"{current_public_ip}",
                "name":     f"{name}",
                "proxied":  False,
                "type":     "A",
                "comment":  f"IP last updated on {current_time} via API User from hostname {hostname}",
                "id":       f"{id}",
                "tags":     [],
                "ttl":      3600
            }
            response = requests.patch(url=url, json=payload, headers=headers)
            if response.status_code != 200:
                print(f'Update Failed: {response.json()}')
            else:
                print(f'IP Successfully updated in CloudFlare!!!')
            return response
        else:
            print(f'The IP Addresses are the same. Not updating')
            return True
    except Exception as e:
        print(f'An issue occurred updating CloudFlare with the current IP: {e}')
        return False

def get_current_public_ip():
    """ Gets the Current Public IP address where this script is running """
    try:
        ip = requests.get('https://api.ipify.org').text
        return ip
    except Exception as e:
        print(f'An issue occurred trying to get the current public IP: {e}')

def get_zone_data():
    """ Pulls Zone data to be used in other functions """
    try:
        print(f'Getting zone data... ')
        headers = get_headers()
        config = get_config()
        zone_name = config['zone_name']
        record_name = config['record_name']
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_name}/dns_records?name={record_name}"
        response = requests.get(url=url, headers=headers)
        json_response = response.json()
        result = json_response["result"][0]
        return result
    except Exception as e:
        print(f'An issue occurred trying to get the zone data: {e}')
        return False

def main():
    try:
        print(f'Starting... ')
        if get_verify_api():
            print(f'Token active... continuing... ')
            current_public_ip = get_current_public_ip()
            zone_data = get_zone_data()
            update_ip_in_cloudflare(current_public_ip=current_public_ip, zone_data=zone_data)
        else:
            print('An issue occurred with Authentication. Is the token typed out or set up correctly?')
        print(f'Complete... ')
    except Exception as e:
        print(f'An issue occurred trying to update the CloudFlare DNS Record: {e}')
        return False

if __name__ == '__main__':
    main()
