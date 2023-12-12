from CloudFlare import CloudFlare
import requests
import json

""" 
Update your DNS record in CloudFlare with your Home IP  
"""

def get_config():
    try:
        # Open the config.json file in read mode
        with open('config.json', 'r') as f:
            
            # Load the JSON data from the file
            config = json.load(f)

            # Return the values as a dictionary
            return config
    except Exception as e:
        print(f'An issue occured trying to open the configuration file: {e}')

def main():
    try:
        # Call the get_config function and assign the values to variables
        config = get_config()
        zone_name = config['zone_name']
        record_name = config['record_name']
        email = config['email']
        token = config['token']

        cf = CloudFlare(email=email,token=token)

        # Get your current public IP address
        ip = requests.get('https://api.ipify.org').text
        
        # Update your DNS record with your current IP address
        dns_record = cf.zones.dns_records.get(cf.zones.get(params={'name': zone_name})[0]['id'], params={'name': record_name})
        dns_record['content'] = ip
        cf.zones.dns_records.put(cf.zones.get(params={'name': zone_name})[0]['id'], dns_record['id'], data=dns_record)
        return True
    except Exception as e:
        print(f'An issue occured trying to update the CloudFlare DNS Record: {e}')
        return False

if __name__ == '__main__':
    main()
