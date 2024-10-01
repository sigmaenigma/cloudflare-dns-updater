# CloudFlare
The app.py Python file can be used to directly update your CloudFlare DNS record with the IP Address of your home network. After detecting if the IP address that is saved in CloudFlare differs from the detected IP address of the host where the app.py file is running, an update is done in CloudFlare with the new IP4 address for a target DNS record.

By default, the main app `app.py` runs on an interval specified in the [config.json](https://github.com/sigmaenigma/CloudFlare/blob/main/DNSRecordUpdate/config.json) file. If you want to run it manually, you can run the `app_manual.py` file.

# Installation
1. git clone https://github.com/sigmaenigma/CloudFlare.git
2. pip install requests

# Configuration
1. Get your API token from CloudFlare and make sure the token is able to be used for edits. Add this to the "token".
2. Get the Zone ID for the domain. This is a 32 digit alphanumeric string. Add this to "zone_name".
3. Add the full subdomain (e.g. test.example.com) to the "record_name".
4. Add your interval setting in interval_minutes. For example, set to 15 if you want the script to run every 15 minutes
5. You can also manually invoke the app by running `python3 app_manual.py`
6. Save

# Running on a timed interval (perpetual)
`python3 app.py`

# Running manually (exits on completion)
`python3 app_manual.py`

# Automation
Up to you how you want to automate but I recommend a cron job that runs hourly. 
