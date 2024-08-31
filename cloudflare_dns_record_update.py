import requests
import json
from datetime import datetime

""" 
Update your DNS record in CloudFlare with your Home IP  
"""

def get_config():
    """ Opens the JSON config file and returns the contents """
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(f'An issue occured trying to open the configuration file: {e}')

def get_verify_api():
    """ Verifies the Token works and returns True if it does """
    try:
        url = f"https://api.cloudflare.com/client/v4/user/tokens/verify"
        headers = get_headers()
        verify_url_response = requests.get(url=url, headers=headers)
        if "result" in verify_url_response.json():
            if verify_url_response.json()['result']['status'] == 'active':
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print(f'An issue occured with get_verify_api(): {e}')
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
        print(f'An issue occured getting headers: {e}')
        return False

def update_ip_in_cloudflare(current_public_ip, cloudflare_ip, name, id, zone_id, force=False):
    """ Updates the IP (content) in CloudFlare if a change is detected or the Force flag is enabled for a given domain name """
    try:
        if current_public_ip != cloudflare_ip or force == True:
            print(f'Updating the CloudFlare IP {cloudflare_ip} with the current public IP: {current_public_ip}')
            current_time = datetime.now()
            headers = get_headers()
            url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{id}"
            payload = {
                "content": f"{current_public_ip}",
                "name": f"{name}",
                "proxied": False,
                "type": "A",
                "comment": f"IP last updated on {current_time} via API User",
                "id": f"{id}",
                "tags": [],
                "ttl": 3600
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
        print(f'An issue occured updating CloudFlare with the current IP: {e}')
        return False

def get_current_public_ip():
    """ Gets the Current Public IP address where this script is running """
    try:
        ip = requests.get('https://api.ipify.org').text
        return ip
    except Exception as e:
        print(f'An issue occured trying to get the current public IP: {e}')

def get_zone_data():
    """ Pulls Zone data to be used in other functions """
    try:
        headers = get_headers()
        config = get_config()
        zone_name = config['zone_name']
        record_name = config['record_name']
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_name}/dns_records?name={record_name}"
        response = requests.get(url=url, headers=headers).json()
        result = response["result"][0]
        return result
    except Exception as e:
        print(f'An issue occured trying to get the zone data: {e}')
        return False

def main():
    try:
        print(f'Starting... ')
        verify_url_response = get_verify_api()
        if verify_url_response:
            print(f'Token active... continuing... ')
            current_public_ip = get_current_public_ip()
            zone_data = get_zone_data()
            update_ip_in_cloudflare(
                current_public_ip=current_public_ip, 
                cloudflare_ip=zone_data["content"], 
                name=zone_data["name"], 
                id=zone_data["id"], 
                zone_id=zone_data["zone_id"],
                force=True
                )
        print(f'Complete... ')
    except Exception as e:
        print(f'An issue occured trying to update the CloudFlare DNS Record: {e}')
        return False

if __name__ == '__main__':
    main()
