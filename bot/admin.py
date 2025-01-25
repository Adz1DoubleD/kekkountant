from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from datetime import datetime, timedelta

from bot import callbacks, constants, db


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in constants.TG_ADMIN_ID:
        settings = db.settings_get_all()
        if not settings:
            await update.message.reply_text("Error fetching settings.")
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    f"{setting.replace('_', ' ').title()}: {'ON' if status else 'OFF'}",
                    callback_data=f"settings_toggle_{setting}"
                )
            ]
            for setting, status in settings.items()
        ]

        keyboard.append(
            [
                InlineKeyboardButton("Reset Clicks", callback_data="question:clicks_reset")
            ]
        )

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Admin Commands:\n\n"
            "/click_me - Sends Click me Instantly\n"
            "/wen - Next click me time", reply_markup=reply_markup)


async def click_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in constants.TG_ADMIN_ID:
        if db.settings_get("click_me"):
            await callbacks.button_send(context)
        else:
            await update.message.reply_text(f"Click Me is disabled")


async def wen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in constants.TG_ADMIN_ID:
        if update.effective_chat.type == "private":
            if db.settings_get("click_me"):
                if constants.BUTTON_TIME is not None:
                    time = constants.BUTTON_TIME
                else:    
                    time = constants.FIRST_BUTTON_TIME
                target_timestamp = constants.RESTART_TIME + time
                time_difference_seconds = target_timestamp - datetime.now().timestamp()
                time_difference = timedelta(seconds=time_difference_seconds)
                hours, remainder = divmod(time_difference.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                await update.message.reply_text(f"Next Click Me:\n\n{hours} hours, {minutes} minutes, {seconds} seconds"
                )
            else:
                await update.message.reply_text(f"Next Click Me:\n\nDisabled\n\n"
                )