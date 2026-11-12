# Local IP Discord Reporter

Send the local IPv4 address used for the default outbound route to a Discord channel once, then exit. This is the machine's LAN address, not its public IP address. A working network connection and access to Discord are required.

## Discord setup

1. Create an application and bot in the [Discord Developer Portal](https://discord.com/developers/applications). Copy its bot token and keep it secret. Reset the token in the portal if it is exposed.
2. Invite the bot to your server using the OAuth2 URL generator with the `bot` scope. Grant it **View Channel** and **Send Messages** for the destination channel. Check any channel-specific permission overrides as well.
3. Enable Developer Mode in Discord's advanced settings. Copy the server ID and channel ID from their context menus.

## Installation

Install Python 3.10 or newer. In this directory, create a virtual environment and install the dependencies:

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and fill in `DISCORD_BOT_TOKEN`, `DISCORD_SERVER_ID`, and `DISCORD_CHANNEL_ID`. Restart the program after changing them. Keep this file private; on Linux, restrict it with `chmod 600 .env`.

Run a manual test from this directory:

```powershell
.\.venv\Scripts\python.exe ip_reporter.py
```

On Linux, run `.venv/bin/python ip_reporter.py` instead. A successful run prints a confirmation and sends one message. Errors are printed to standard error and produce a nonzero exit code. The file is loaded relative to the script, so the working directory can differ. Existing environment variables take precedence over `.env`.

## Start automatically on Windows

In Task Scheduler, create a task with a trigger **At startup** and an action **Start a program**. Set **Program/script** to the absolute path to `.venv\Scripts\python.exe`, **Add arguments** to the quoted absolute path to `ip_reporter.py`, and **Start in** to the project directory. Configure the task to run under an account that can read the project and `.env`. In the task's Conditions, enable **Start only if the following network connection is available**, and in Settings enable retries if startup fails. Run the task manually once to verify its result and the Discord message.

## Start automatically on Linux

Create `/etc/systemd/system/ip-reporter.service`, replacing `YOUR_USER` and `/absolute/path/to/project` with the account and project path. Use absolute paths without spaces in this example:

```ini
[Unit]
Description=Report local IP to Discord
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
User=YOUR_USER
WorkingDirectory=/absolute/path/to/project
ExecStart=/absolute/path/to/project/.venv/bin/python /absolute/path/to/project/ip_reporter.py
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

Enable the appropriate network manager's wait-online service so `network-online.target` actually waits for connectivity. Then run `sudo systemctl daemon-reload`, `sudo systemctl enable --now ip-reporter.service`, and check `journalctl -u ip-reporter.service`. The task runs at boot and retries failures; systemd's start-rate limits can stop repeated retries. Ensure the configured account can read the project and `.env`.
