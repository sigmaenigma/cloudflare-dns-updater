# CloudFlare DNS Updater

This Python script updates your CloudFlare DNS record with the IP address of your home network. It detects if the IP address saved in CloudFlare differs from the detected IP address of the host where the script is running and updates CloudFlare with the new IPv4 address for a target DNS record.

By default, the main app `app.py` runs on an interval specified in the `config.json` file. If you want to run it manually, you can run the `app_manual.py` file which exists upon completion.

## Prerequisites
- Python 3.x (_If running manually and not using Docker_)
- Docker (for Docker installation) [Docker Website](https://www.docker.com/)
- CloudFlare account with API token [CloudFlare Instructions to Create a Token](https://developers.cloudflare.com/fundamentals/api/get-started/create-token)

## Configuration (`config.json`)
1. **"token"**: Get your API token from CloudFlare and ensure it has edit permissions. 
2. **"zone_name"**: Get the Zone ID for the domain (a 32-digit alphanumeric string).
3. **"record_name"**: Add the full subdomain (e.g., `test.example.com`).
4. **"force_update"**: Set to `true` to bypass the IP comparison check.
5. **"interval_minutes"**: Set the interval for how often to connect to the CloudFlare API (e.g., `15` for every 15 minutes).
6. Save the file.

Example `config.json`:
```json
{
  "token": "your_api_token",
  "zone_name": "your_zone_id",
  "record_name": "test.example.com",
  "force_update": true,
  "interval_minutes": 15
}
```

## Installation (Docker)
1. Clone the repository:
    ```bash
    git clone https://github.com/sigmaenigma/cloudflare-dns-updater.git
    ```
2. Modify the `config.json` file following the [Configuration](#configuration-configjson) instructions above.
3. Build and start the Docker container:
    ```bash
    docker-compose up -d
    ```

## Installation (Python Standalone)
1. Clone the repository:
    ```bash
    git clone https://github.com/sigmaenigma/cloudflare-dns-updater.git
    ```
2. Install the `requests` package:
    ```bash
    pip install requests
    ```
3. Modify the `config.json` file following the [Configuration](#configuration-configjson) instructions above.

## Running on a Timed Interval (Perpetual)
```bash
python3 app.py
```

## Running Manually (Exits on Completion)
```bash
python3 app_manual.py
```
