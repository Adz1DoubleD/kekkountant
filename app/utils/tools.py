import os
import random
import requests
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
    hours = db.get_click_time()
    if hours == 0:
        return None
    seconds = hours * 60 * 60
    if seconds < 1800:
        return None
    time = random.randint(1800, seconds)
    return time


def random_logo():
    random_logo = random.choice(images.LOGOS)
    return random_logo


def update_bot_commands():
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

    user_response = requests.post(
        url, json={"commands": general_commands, "scope": {"type": "default"}}
    )

    general_result = (
        "✅ General commands updated"
        if user_response.status_code == 200
        else f"⚠️ Failed to update general commands: {user_response.text}"
    )

    failed_admins = []
    for admin_id in constants.TG_ADMIN_ID:
        admin_response = requests.post(
            url,
            json={
                "commands": all_commands,
                "scope": {"type": "chat", "chat_id": int(admin_id)},
            },
        )

        if admin_response.status_code != 200:
            failed_admins.append(f"{admin_id}: {admin_response.text}")

    if not failed_admins:
        admin_result = "✅ Admin commands updated"
    else:
        admin_result = "⚠️ Failed to update commands for some admins:\n" + "\n".join(
            failed_admins
        )

    return general_result, admin_result
