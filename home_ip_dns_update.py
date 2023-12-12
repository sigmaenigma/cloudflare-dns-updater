from CloudFlare import CloudFlare
import requests

""" 
Update your DNS record in CloudFlare with your Home IP  
"""

def main():
    try:
        # Set your domain name and record name
        zone_name = 'example.com'
        record_name = 'home.example.com'
        # Set your Cloudflare API key and email
        email='your-email@example.com'
        token='your-api-key'

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
