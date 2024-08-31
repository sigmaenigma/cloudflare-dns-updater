# CloudFlare
The cloudflare_dns_record_update.py Python file can be used to directly update your CloudFlare DNS record with the IP Address of your home network. This can be run as a cron job

# Installation
1. git clone https://github.com/sigmaenigma/CloudFlare.git
2. pip install requests

# Configuration
1. Get your API token from CloudFlare and make sure the token is able to be used for edits. Add this to the "token".
2. Get the Zone ID for the domain. This is a 32 digit alphanumeric string. Add this to "zone_name".
3. Add the full subdomain (e.g. test.example.com) to the "record_name".
4. Save

# Running
python cloudflare_dns_record_update.py

# Automation
Up to you how you want to automate but I recommend a cron job that runs hourly. 
