from CloudFlare import CloudFlare
import requests
import json
import ipaddress # import the ipaddress module

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
        
        # Get your old IP address from the DNS record
        dns_record = cf.zones.dns_records.get(cf.zones.get(params={'name': zone_name})[0]['id'], params={'name': record_name})
        old_ip = dns_record['content']

        # Convert the IP addresses to ipaddress objects
        ip = ipaddress.ip_address(ip)
        old_ip = ipaddress.ip_address(old_ip)

        # Check if the IP addresses are different
        if ip != old_ip:
            # Update your DNS record with your current IP address
            dns_record['content'] = str(ip) # convert the ip object to a string
            cf.zones.dns_records.put(cf.zones.get(params={'name': zone_name})[0]['id'], dns_record['id'], data=dns_record)
            print(f'IP address changed from {old_ip} to {ip}. DNS record updated.')
        else:
            # No need to update the DNS record
            print(f'IP address is still {ip}. No change needed.')
        return True
    except Exception as e:
        print(f'An issue occured trying to update the CloudFlare DNS Record: {e}')
        return False

if __name__ == '__main__':
    main()
