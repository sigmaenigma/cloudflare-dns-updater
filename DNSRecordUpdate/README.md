# CloudFlare
The app.py Python file can be used to directly update your CloudFlare DNS record with the IP Address of your home network. After detecting if the IP address that is saved in CloudFlare differs from the detected IP address of the host where the app.py file is running, an update is done in CloudFlare with the new IPV4 address for a target DNS record.

By default, the main app `app.py` runs on an interval specified in the [config.json](https://github.com/sigmaenigma/CloudFlare/blob/main/DNSRecordUpdate/config.json) file. If you want to run it manually, you can run the `app_manual.py` file.

## Configuration (config.json)
1. **"token"**: Get your API token from CloudFlare and make sure the token is able to be used for edits.
2. **"zone_name"**: Get the Zone ID for the domain. This is a 32 digit alphanumeric string.
3. **"record_name"**: Add the full subdomain (e.g. test.example.com).
4. **"force_update"**: Force Update should be set to True if you want to bypass the IP comparison check.
5. **"interval_minutes"**: Add your interval setting for how often to connect to the CloudFlare API. For example, set to 15 if you want the script to run every 15 minutes.
7. Save

# Installation (Python Standalone)
1. `git clone https://github.com/sigmaenigma/CloudFlare.git`
2. Install requests package `pip install requests`
3. Navigate to the DNSRecordUpdate directory `cd DNSRecordUpdate`
4. Modify the [config.json](https://github.com/sigmaenigma/CloudFlare/blob/main/DNSRecordUpdate/config.json) file following the Configuration instructions above.

## Running on a timed interval (perpetual)
`python3 app.py`

## Running manually (exits on completion)
`python3 app_manual.py`

# Installation (Docker runs perpetually when started)
1. `git clone https://github.com/sigmaenigma/CloudFlare.git`
2. Navigate to the DNSRecordUpdate directory `cd DNSRecordUpdate`
3. Modify the [config.json](https://github.com/sigmaenigma/CloudFlare/blob/main/DNSRecordUpdate/config.json) file following the [Configuration](https://github.com/sigmaenigma/CloudFlare/blob/main/DNSRecordUpdate/README.md#configuration-configjson) instructions above
4. Run `docker-compose up -d` to build and start cf-dns-updater.
