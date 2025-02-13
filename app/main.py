from telegram import Update, Message
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

import os
from telegram.warnings import PTBUserWarning
from warnings import filterwarnings

from bot import callbacks, conversations
from bot.commands import admin, general
from utils import tools
from services import get_dbmanager

db = get_dbmanager()

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)

application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
job_queue = application.job_queue


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return


async def error(update: Update, context):
    if update is None:
        return
    if update.edited_message is not None:
        return
    else:
        message: Message = update.message
        if message is not None and message.text is not None:
            print(f"{message.text} caused error: {context.error}")

        else:
            print(f"Error occurred without a valid message: {context.error}")


def init_bot():
    application.add_error_handler(error)

    for cmd, handler, _ in general.HANDLERS:
        if isinstance(cmd, list):
            for alias in cmd:
                application.add_handler(CommandHandler(alias, handler))
        else:
            application.add_handler(CommandHandler(cmd, handler))

    for cmd, handler, _ in admin.HANDLERS:
        application.add_handler(CommandHandler(cmd, handler))

    for handler, pattern in callbacks.HANDLERS:
        application.add_handler(CallbackQueryHandler(handler, pattern=pattern))

    for handler in conversations.HANDLERS:
        application.add_handler(
            ConversationHandler(
                entry_points=handler["entry_points"],
                states=handler["states"],
                fallbacks=handler.get(
                    "fallbacks",
                    [],
                ),
            )
        )

    for handler_data in conversations.HANDLERS:
        application.add_handler(
            ConversationHandler(
                entry_points=handler_data["entry_points"],
                states=handler_data["states"],
                fallbacks=handler_data.get("fallbacks", []),
            )
        )


def start():
    print("🔄 Initializing bot...")
    init_bot()

    if not tools.is_local():
        print("✅ Bot Running on server")

        general_commands, admin_commands = tools.update_bot_commands()
        print(general_commands)
        print(admin_commands)

    else:
        print("✅ Bot Running locally")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    start()
