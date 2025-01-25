from telegram import Update, Message
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

import os

from bot import admin, commands, callbacks, settings

application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
job_queue = application.job_queue


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


if __name__ == "__main__":
    application.add_error_handler(error)
    
    application.add_handler(CommandHandler("admin", admin.command))
    application.add_handler(CommandHandler("reset", admin.reset))
    application.add_handler(CommandHandler("click_me", admin.click_me))
    application.add_handler(CommandHandler("wen", admin.wen))

    application.add_handler(CommandHandler("ascii", commands.ascii))
    application.add_handler(CommandHandler("buy", commands.buy))
    application.add_handler(CommandHandler("ca", commands.ca))
    application.add_handler(CommandHandler("chart", commands.chart))
    application.add_handler(CommandHandler("coinflip", commands.ascii))
    application.add_handler(CommandHandler("daily", commands.daily))
    application.add_handler(CommandHandler("joke", commands.joke))
    application.add_handler(CommandHandler("leaderboard", commands.leaderboard))
    application.add_handler(CommandHandler("me", commands.me))
    application.add_handler(CommandHandler("roll", commands.roll))
    application.add_handler(CommandHandler("say", commands.say))
    application.add_handler(CommandHandler("twitter", commands.twitter))
    application.add_handler(CommandHandler("website", commands.website))

    application.add_handler(CallbackQueryHandler(callbacks.button_click, pattern=r"^click_button:\d+$"))

    job_queue.run_once(
        callbacks.button_send,
        settings.FIRST_BUTTON_TIME,
        settings.TG_CHANNEL_ID,
        name="Click Me",
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)
