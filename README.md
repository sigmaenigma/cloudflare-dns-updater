# CloudFlare DNS Updater

Keeps a Cloudflare A record pointed at the public IPv4 address of the network this runs on, like a dynamic DNS client. Each cycle it looks up the host's public IP, compares it with the record in Cloudflare, and updates the record only when they differ. The record's proxied status and TTL are left untouched.

- `app.py` runs forever and checks on the interval set in `config.json`.
- `app_manual.py` runs one check and exits. It exits non-zero on failure, so it works well under cron or as a quick test.

## Prerequisites
- A Cloudflare account and an API token ([how to create one](https://developers.cloudflare.com/fundamentals/api/get-started/create-token)). Give the token the minimum it needs: **Zone → DNS → Edit**, restricted to the single zone that holds the record. Do not use the Global API Key.
- The A record must already exist in Cloudflare. This script updates it; it does not create it.
- Docker, or Python 3.10 or newer if running standalone.

## Configuration
1. Copy the example file:
    ```bash
    cp config.example.json config.json
    ```
2. Fill in the values:
    - **`zone_id`**: the Zone ID of your domain, shown on the zone's Overview page in the Cloudflare dashboard.
    - **`dns_record_name`**: the full record name, for example `home.example.com`.
    - **`token`**: your API token. You can leave this out and set the `CF_API_TOKEN` environment variable instead, which takes precedence.
    - **`force_update`**: `false` by default. `true` writes the record every cycle even when the IP has not changed. Leave it `false` unless you are debugging.
    - **`interval_minutes`**: how often to check. Defaults to `15`.

`config.json` is in `.gitignore` so a real token is never committed. Keep it that way.

## Running with Docker
```bash
docker compose up -d --build
docker compose logs -f
```
The container runs as an unprivileged user, so `config.json` must be readable by other users on the host (for example `chmod 644 config.json`). If you would rather keep the file private with `chmod 600`, remove `token` from it and pass `CF_API_TOKEN` through the `environment` block in `docker-compose.yml` or a `.env` file instead.

Make sure `config.json` exists before the first `docker compose up`. If it is missing, Docker creates an empty directory with that name on the host and the app fails to start.

The app reads its config once at startup. After editing `config.json`, run `docker compose restart`.

## Running standalone
```bash
pip install -r requirements.txt
python3 app.py          # checks on an interval, runs until stopped
python3 app_manual.py   # one check, then exits
```
By default the app looks for `config.json` next to `app.py`. Set `CONFIG_FILE=/path/to/config.json` to use a different location.

## Notes
- IPv4 only. The public IP is looked up through `api.ipify.org` and the script updates A records only.
- Each update sets the record's comment to a timestamp and the hostname that made the change, which you can see in the Cloudflare dashboard.
- If the token is invalid at startup, the app logs the reason and exits with code 1. Failures during a check cycle are logged and the app waits for the next cycle.
