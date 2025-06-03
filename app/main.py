from telegram import Update, Message
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

import os
from telegram.warnings import PTBUserWarning
from warnings import filterwarnings

from bot import callbacks, constants
from bot.commands import admin, general
from utils import tools
from services import get_dbmanager

db = get_dbmanager()

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)

application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
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
    print("🔄 Initializing main bot...")
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

    print("✅ Main bot initialized")


async def post_init(application: Application):
    if not tools.is_local():
        print("✅ Bot Running on server")
        if constants.ENABLED:
            application.job_queue.run_once(
                callbacks.button_send,
                constants.FIRST_BUTTON_TIME,
                constants.TG_CHANNEL_ID,
                name="Click Me",
            )

        print(await tools.update_bot_commands())

    else:
        print("✅ Bot Running locally")


if __name__ == "__main__":
    init_bot()
    application.post_init = post_init
    application.run_polling(allowed_updates=Update.ALL_TYPES)
