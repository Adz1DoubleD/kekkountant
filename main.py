from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

import os

from bot import callbacks, commands, settings

application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
job_queue = application.job_queue


if __name__ == "__main__":
    application.add_handler(CommandHandler("reset", commands.reset))
    application.add_handler(CommandHandler("click_me", commands.click_me))
    application.add_handler(CommandHandler("leaderboard", commands.leaderboard))
    application.add_handler(CommandHandler("me", commands.me))
    application.add_handler(CommandHandler("wen", commands.wen))

    job_queue.run_once(
        callbacks.button_send,
        settings.FIRST_BUTTON_TIME,
        settings.TG_CHANNEL_ID,
        name="Click Me",
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)
