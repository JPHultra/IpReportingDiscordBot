"""Send this machine's outbound local IPv4 address to a Discord channel."""

import asyncio
import os
import socket
import sys
from pathlib import Path

import discord
from dotenv import load_dotenv


def configuration():
    load_dotenv(Path(__file__).resolve().parent / ".env")
    token = os.getenv("DISCORD_BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("DISCORD_BOT_TOKEN is required")
    ids = []
    for name in ("DISCORD_SERVER_ID", "DISCORD_CHANNEL_ID"):
        value = os.getenv(name, "").strip()
        if not value.isascii() or not value.isdecimal() or int(value) <= 0:
            raise ValueError(f"{name} must be a positive numeric Discord ID")
        ids.append(int(value))
    return token, *ids


def local_ipv4():
    # UDP connect selects a route without sending a packet.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(("8.8.8.8", 80))
        address = sock.getsockname()[0]
    if address.startswith("127.") or address == "0.0.0.0":
        raise OSError("No usable outbound IPv4 address found")
    return address


async def report(token, server_id, channel_id):
    address = local_ipv4()
    hostname = socket.gethostname()
    client = discord.Client(intents=discord.Intents.none())
    completed = False

    @client.event
    async def on_ready():
        nonlocal completed
        if completed:
            return
        completed = True
        try:
            channel = await client.fetch_channel(channel_id)
            if getattr(getattr(channel, "guild", None), "id", None) != server_id:
                raise ValueError("Channel does not belong to the configured server")
            await channel.send(f"Machine `{hostname}` local IPv4: `{address}`")
            print(f"Reported local IPv4 for {hostname}.")
        finally:
            await client.close()

    # Exceptions in event callbacks are normally logged and swallowed by discord.py.
    # Capture them so the process can return a useful failure status.
    errors = []

    @client.event
    async def on_error(event, *args, **kwargs):
        errors.append(sys.exc_info()[1])
        await client.close()

    try:
        await asyncio.wait_for(client.start(token, reconnect=False), timeout=60)
    finally:
        await client.close()
    if errors:
        raise errors[0]
    if not completed:
        raise RuntimeError("Discord connection closed before the report was sent")


def main():
    try:
        asyncio.run(report(*configuration()))
    except (Exception, KeyboardInterrupt) as exc:
        print(f"IP report failed: {exc or type(exc).__name__}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
