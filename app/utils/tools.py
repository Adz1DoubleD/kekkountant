import aiohttp
import os
import random
import socket

from bot import constants
from bot.commands import admin, general
from media import images
from services import get_dbmanager


db = get_dbmanager()


def escape_markdown(text):
    characters_to_escape = ["*", "_", "`"]
    for char in characters_to_escape:
        text = text.replace(char, "\\" + char)
    return text


def format_seconds(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    if minutes > 0:
        return f"{minutes} minutes and {remaining_seconds:.0f} seconds"
    else:
        return f"{remaining_seconds:.3f} seconds"


def is_local():
    ip = socket.gethostbyname(socket.gethostname())
    return ip.startswith("127.") or ip.startswith("192.168.") or ip == "localhost"


def random_button_time():
    time = random.randint(3600, constants.MAX_CLICK_SECONDS)
    return time


def random_logo():
    random_logo = random.choice(images.LOGOS)
    return random_logo


async def update_bot_commands():
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/setMyCommands"

    general_commands = [
        {
            "command": cmd[0] if isinstance(cmd, list) else cmd,
            "description": desc,
        }
        for cmd, _, desc in general.HANDLERS
    ]

    admin_commands = [
        {"command": cmd, "description": desc} for cmd, _, desc in admin.HANDLERS
    ]

    all_commands = general_commands + admin_commands
    results = []
    failed_admins = []

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, json={"commands": general_commands, "scope": {"type": "default"}}
        ) as response:
            results.append(
                "✅ General commands updated"
                if response.status == 200
                else f"⚠️ Failed to update commands: {await response.text()}"
            )

        for admin_id in constants.TG_ADMIN_ID:
            try:
                async with session.post(
                    url,
                    json={
                        "commands": all_commands,
                        "scope": {"type": "chat", "chat_id": int(admin_id)},
                    },
                ) as response:
                    if response.status == 200:
                        results.append(f"✅ Admin commands updated for {admin_id}")
                    else:
                        failed_admins.append(admin_id)
                        results.append(
                            f"⚠️ Failed to update Admin commands for {admin_id}: {await response.text()}"
                        )
            except Exception as e:
                failed_admins.append(admin_id)
                results.append(
                    f"⚠️ Error updating Admin commands for {admin_id}: {str(e)}"
                )

    if failed_admins:
        results.append(
            f"❌ Failed to update commands for admins: {', '.join(str(id) for id in failed_admins)}"
        )

    return "\n".join(results)
