from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    MessageHandler,
)

from bot.commands import admin
from bot import constants
from services import get_dbmanager

db = get_dbmanager()


CLICKS_TIME_SET = 1


async def clicks_time_set_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in constants.TG_ADMIN_ID:
        await query.answer(text="Admin only.", show_alert=True)
        return

    await query.answer()

    await query.message.reply_text(
        "Send the maximum number of hours you want to set Click Me to:\n\n0 is off",
    )

    return CLICKS_TIME_SET


async def clicks_time_set_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in constants.TG_ADMIN_ID:
        await update.message.reply_text("Admin only.")
        return ConversationHandler.END

    try:
        new_value = int(update.message.text)
        db.set_click_time(new_value)

        await update.message.reply_text(f"Click Me max time updated to {new_value}.")

        await admin.command(update, context)

    except ValueError:
        await update.message.reply_text("Invalid number. Please enter a valid integer.")

    return ConversationHandler.END


HANDLERS = [
    {
        "entry_points": [
            CallbackQueryHandler(clicks_time_set_1, pattern="^clicks_time_set$")
        ],
        "states": {
            CLICKS_TIME_SET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, clicks_time_set_2)
            ],
        },
        "fallbacks": [],
    }
]
