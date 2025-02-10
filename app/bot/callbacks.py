from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import random
import time
from datetime import datetime

from bot import admin, constants
from main import application
from utils import tools
from services import get_dbmanager

db = get_dbmanager()

job_queue = application.job_queue

CLICKS_TIME_SET = 1


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button_click_timestamp = time.time()

    current_button_data = context.bot_data.get("current_button_data")
    if not current_button_data or update.callback_query.data != current_button_data:
        return

    button_generation_timestamp = context.bot_data.get("button_generation_timestamp")
    if not button_generation_timestamp:
        await update.callback_query.answer("Too slow!", show_alert=True)
        return

    if context.bot_data.get("first_user_clicked"):
        await update.callback_query.answer("Too slow!", show_alert=True)
        return

    user = update.effective_user
    user_info = (
        user.username or f"{user.first_name} {user.last_name}" or user.first_name
    )

    time_taken = button_click_timestamp - button_generation_timestamp
    formatted_time_taken = tools.format_seconds(time_taken)

    await db.update_clicks(user_info, time_taken)

    context.bot_data["first_user_clicked"] = True

    user_data = db.get_by_name(user_info)
    clicks, _, streak = user_data
    total_click_count = db.get_total_clicks()

    if clicks == 1:
        user_count_message = "🎉🎉 This is their first button click! 🎉🎉"
    elif clicks % 10 == 0:
        user_count_message = f"🎉🎉 They have been the fastest player {clicks} times and on a *{streak}* click streak! 🎉🎉"
    else:
        user_count_message = f"They have been the fastest player {clicks} times and on a *{streak}* click streak!"

    if db.check_is_fastest(time_taken):
        user_count_message += (
            f"\n\n🎉🎉 {formatted_time_taken} is the new fastest time! 🎉🎉"
        )

    message_text = (
        f"@{tools.escape_markdown(user_info)} was the fastest player in {formatted_time_taken}!\n\n"
        f"{user_count_message}\n\n"
        f"The button has been clicked a total of {total_click_count} times by all players!\n\n"
        f"use `/leaderboard` to see the fastest players!"
    )

    photos = await context.bot.get_user_profile_photos(
        update.effective_user.id, limit=1
    )
    if photos and photos.photos and photos.photos[0]:
        photo = photos.photos[0][0].file_id
        clicked = await context.bot.send_photo(
            photo=photo,
            chat_id=update.effective_chat.id,
            caption=message_text,
            parse_mode="Markdown",
        )
    else:
        clicked = await context.bot.send_message(
            chat_id=update.effective_chat.id, text=message_text, parse_mode="Markdown"
        )

    context.bot_data["clicked_id"] = clicked.message_id
    constants.RESTART_TIME = datetime.now().timestamp()
    constants.BUTTON_TIME = tools.random_button_time()
    job_queue.run_once(
        button_send,
        constants.BUTTON_TIME,
        chat_id=constants.TG_CHANNEL_ID,
        name="Click Me",
    )


async def button_send(context: ContextTypes.DEFAULT_TYPE):
    if not db.get_click_time():
        return

    context.bot_data["first_user_clicked"] = False

    previous_click_me_id = context.bot_data.get("click_me_id")
    previous_clicked_id = context.bot_data.get("clicked_id")

    if previous_click_me_id:
        try:
            await context.bot.delete_message(
                chat_id=constants.TG_CHANNEL_ID, message_id=previous_click_me_id
            )
            await context.bot.delete_message(
                chat_id=constants.TG_CHANNEL_ID, message_id=previous_clicked_id
            )
        except Exception:
            pass

    current_button_data = str(random.randint(1, 100000000))
    context.bot_data["current_button_data"] = f"click_button:{current_button_data}"

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Click Me!", callback_data=context.bot_data["current_button_data"]
                )
            ]
        ]
    )
    click_me = await context.bot.send_photo(
        photo=tools.random_logo(),
        chat_id=constants.TG_CHANNEL_ID,
        reply_markup=keyboard,
    )

    context.bot_data["button_generation_timestamp"] = time.time()
    context.bot_data["click_me_id"] = click_me.message_id


async def clicks_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in constants.TG_ADMIN_ID:
        await query.answer(text="Admin only.", show_alert=True)
        return

    try:
        result_text = db.reset_leaderboard()
        await query.edit_message_text(text=result_text)
    except Exception as e:
        await query.answer(text=f"An error occurred: {str(e)}", show_alert=True)


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


async def question_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    try:
        await query.edit_message_text(text="Action canceled. No changes were made.")
    except Exception:
        await update.message.reply_text(text="Action canceled. No changes were made.")

    return ConversationHandler.END


async def question_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data=None
):
    query = update.callback_query

    callback_data = callback_data or query.data
    question = callback_data.split(":")[1]

    replies = {
        "clicks_reset": "Are you sure you want to reset clicks?",
    }

    reply = replies.get(question)

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=question),
            InlineKeyboardButton("No", callback_data="cancel"),
        ]
    ]

    await query.edit_message_text(
        text=reply, reply_markup=InlineKeyboardMarkup(keyboard)
    )
