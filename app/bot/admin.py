from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from datetime import datetime, timedelta

from bot import callbacks, constants
from hooks import db


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in constants.TG_ADMIN_ID:
        click_me_value = db.clicks_time_get()

        keyboard = [
            [
                InlineKeyboardButton(
                    "Change Click Me max time", callback_data="clicks_time_set"
                )
            ],
            [
                InlineKeyboardButton(
                    "Reset Clicks", callback_data="question:clicks_reset"
                )
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        if click_me_value == 0:
            click_me_str = "Off"
        else:
            click_me_str = f"{click_me_value} hours"
        await update.message.reply_text(
            "Click Me Settings:\n\n"
            f"Click Me max time - {click_me_str}\n"
            "/click_me - Sends Click Me Instantly\n"
            "/wen - Next Click Me Time",
            reply_markup=reply_markup,
        )


async def click_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in constants.TG_ADMIN_ID:
        if db.clicks_time_get():
            await callbacks.button_send(context)
        else:
            await update.message.reply_text("Click Me is disabled")


async def wen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in constants.TG_ADMIN_ID:
        if update.effective_chat.type == "private":
            if db.clicks_time_get():
                if constants.BUTTON_TIME is not None:
                    time = constants.BUTTON_TIME
                else:
                    time = constants.FIRST_BUTTON_TIME
                target_timestamp = constants.RESTART_TIME + time
                time_difference_seconds = target_timestamp - datetime.now().timestamp()
                time_difference = timedelta(seconds=time_difference_seconds)
                hours, remainder = divmod(time_difference.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                await update.message.reply_text(
                    f"Next Click Me:\n\n{hours} hours, {minutes} minutes, {seconds} seconds"
                )
            else:
                await update.message.reply_text("Next Click Me:\n\nDisabled\n\n")
