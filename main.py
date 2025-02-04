from telegram import Update, Message
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

import os

from bot import admin, commands, callbacks, constants, db, tools

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


if __name__ == "__main__":
    application.add_error_handler(error)

    application.add_handler(CommandHandler(["click_me", "clickme"], admin.click_me))
    application.add_handler(CommandHandler("settings", admin.command))
    application.add_handler(CommandHandler("wen", admin.wen))

    application.add_handler(CommandHandler("ascii", commands.ascii))
    application.add_handler(CommandHandler("buy", commands.buy))
    application.add_handler(CommandHandler("ca", commands.ca))
    application.add_handler(CommandHandler("chart", commands.chart))
    application.add_handler(CommandHandler("coinflip", commands.coinflip))
    application.add_handler(CommandHandler("daily", commands.daily))
    application.add_handler(CommandHandler("fact", commands.fact))
    application.add_handler(CommandHandler("joke", commands.joke))
    application.add_handler(CommandHandler("leaderboard", commands.leaderboard))
    application.add_handler(CommandHandler("me", commands.me))
    application.add_handler(CommandHandler("roll", commands.roll))
    application.add_handler(CommandHandler("say", commands.say))
    application.add_handler(CommandHandler("twitter", commands.twitter))
    application.add_handler(CommandHandler("website", commands.website))

    application.add_handler(CallbackQueryHandler(callbacks.button_click, pattern=r"^click_button:\d+$"))
    application.add_handler(CallbackQueryHandler(callbacks.clicks_reset, pattern="^clicks_reset$"))
    application.add_handler(CallbackQueryHandler(callbacks.question_cancel, pattern="^cancel$"))
    application.add_handler(CallbackQueryHandler(callbacks.question_confirm, pattern="^question:.*"))

    clicks_time_set_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(callbacks.clicks_time_set_1, pattern="^clicks_time_set$")],
        states={
            callbacks.CLICKS_TIME_SET: [MessageHandler(filters.TEXT & ~filters.COMMAND, callbacks.clicks_time_set_2)],
        },
        fallbacks=[],
    )
    application.add_handler(clicks_time_set_handler)

    if not tools.is_local():
        print("Running on server")
        if db.clicks_time_get():
            job_queue.run_once(
                callbacks.button_send,
                constants.FIRST_BUTTON_TIME,
                constants.TG_CHANNEL_ID,
                name="Click Me",
            )
        
    else:
        application.add_handler(CommandHandler("test", test_command))
        print("Running Bot locally for testing")

    application.run_polling(allowed_updates=Update.ALL_TYPES)
