from telegram import Update
from telegram.ext import ContextTypes

from datetime import datetime, timedelta

from bot import callbacks, db, settings


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in settings.TG_ADMIN_ID:
        await update.message.reply_text(
            "Admin Commands:\n\n"
            "/click_me\n"
            "/reset\n"
            "/wen")


async def click_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in settings.TG_ADMIN_ID:
        await callbacks.button_send(context)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in settings.TG_ADMIN_ID:
        db.clicks_reset()
        await update.message.reply_text("Clicks Reset")


async def wen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in settings.TG_ADMIN_ID:
        if update.effective_chat.type == "private":
            if settings.BUTTON_TIME is not None:
                time = settings.BUTTON_TIME
            else:    
                time = settings.FIRST_BUTTON_TIME
            target_timestamp = settings.RESTART_TIME + time
            time_difference_seconds = target_timestamp - datetime.now().timestamp()
            time_difference = timedelta(seconds=time_difference_seconds)
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            await update.message.reply_text(f"Next Click Me:\n\n{hours} hours, {minutes} minutes, {seconds} seconds\n\n"
            )