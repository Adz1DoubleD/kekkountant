from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import os, random, time
from datetime import datetime

from bot import constants, db, tools
from main import application

job_queue = application.job_queue


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button_click_timestamp = time.time()

    current_button_data = context.bot_data.get("current_button_data")
    if not current_button_data or update.callback_query.data != current_button_data:
        return

    button_generation_timestamp = context.bot_data.get("button_generation_timestamp")
    if not button_generation_timestamp:
        await update.callback_query.answer("Too slow!", show_alert=True)
        return

    button_data = update.callback_query.data
    user = update.effective_user
    user_info = user.username or f"{user.first_name} {user.last_name}" or user.first_name

    context.user_data.setdefault("clicked_buttons", set())
    if button_data in context.user_data["clicked_buttons"]:
        await update.callback_query.answer("You have already clicked this button.", show_alert=True)
        return

    context.user_data["clicked_buttons"].add(button_data)

    if button_data == current_button_data:
        time_taken = button_click_timestamp - button_generation_timestamp

        await db.clicks_update(user_info, time_taken)

        if not context.bot_data.get("first_user_clicked"):
            context.bot_data["first_user_clicked"] = True

            user_data = db.clicks_get_by_name(user_info)
            clicks, _, streak = user_data
            total_click_count = db.clicks_get_total()

            if clicks == 1:
                user_count_message = "🎉🎉 This is their first button click! 🎉🎉"
            elif clicks % 10 == 0:
                user_count_message = f"🎉🎉 They have been the fastest player {clicks} times and on a *{streak}* click streak! 🎉🎉"
            else:
                user_count_message = f"They have been the fastest player {clicks} times and on a *{streak}* click streak!"

            if db.clicks_check_is_fastest(time_taken):
                user_count_message += f"\n\n🎉🎉 {time_taken:.3f} seconds is the new fastest time! 🎉🎉"

            message_text = (
                f"@{tools.escape_markdown(user_info)} was the fastest player in {time_taken:.3f} seconds!\n\n"
                f"{user_count_message}\n\n"
                f"The button has been clicked a total of {total_click_count} times by all players!\n\n"
                f"use `/leaderboard` to see the fastest players!"
            )

            photos = await context.bot.get_user_profile_photos(update.effective_user.id, limit=1)
            if photos and photos.photos and photos.photos[0]:
                photo = photos.photos[0][0].file_id
                clicked = await context.bot.send_photo(
                    photo=photo,
                    chat_id=update.effective_chat.id,
                    caption=message_text,
                    parse_mode="Markdown"
                )
            else:
                clicked = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message_text,
                    parse_mode="Markdown"
                )


            context.bot_data['clicked_id'] = clicked.message_id
            constants.RESTART_TIME = datetime.now().timestamp()
            constants.BUTTON_TIME = tools.random_button_time()
            job_queue.run_once(
                button_send,
                constants.BUTTON_TIME,
                chat_id=constants.TG_CHANNEL_ID,
                name="Click Me",
            )


async def clicks_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if not user_id in constants.TG_ADMIN_ID:
        await query.answer(
            text="Admin only.",
            show_alert=True
        )
        return

    try:
        result_text = db.clicks_reset()
        await query.edit_message_text(
            text=result_text
        )
    except Exception as e:
        await query.answer(
            text=f"An error occurred: {str(e)}",
            show_alert=True
        )


async def button_send(context: ContextTypes.DEFAULT_TYPE):
    if not db.settings_get("click_me"):
        return
    
    context.bot_data["first_user_clicked"] = False

    previous_click_me_id = context.bot_data.get('click_me_id')
    previous_clicked_id = context.bot_data.get('clicked_id')

    if previous_click_me_id:
        try:
            await context.bot.delete_message(chat_id=constants.TG_CHANNEL_ID, message_id=previous_click_me_id)
            await context.bot.delete_message(chat_id=constants.TG_CHANNEL_ID, message_id=previous_clicked_id)
        except Exception:
            pass

    current_button_data = str(random.randint(1, 100000000))
    context.bot_data["current_button_data"] = f"click_button:{current_button_data}"

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Click Me!", callback_data=context.bot_data["current_button_data"])]]
    )
    click_me = await context.bot.send_photo(
        photo=tools.random_logo(),
        chat_id=constants.TG_CHANNEL_ID,
        reply_markup=keyboard,
    )

    context.bot_data["button_generation_timestamp"] = time.time()
    context.bot_data['click_me_id'] = click_me.message_id


async def question_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    try:
        await query.edit_message_text(
            text="Action canceled. No changes were made."
        )
    except Exception as e:
        await update.message.reply_text(
            text="Action canceled. No changes were made."
        )

    return ConversationHandler.END


async def question_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data=None):
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
        text=reply,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def settings_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if not user_id in constants.TG_ADMIN_ID:
        await query.answer(
            text="Admin only.",
            show_alert=True
        )
        return

    callback_data = query.data

    setting = callback_data.replace("settings_toggle_", "")

    try:
        current_status = db.settings_get(setting)
        new_status = not current_status
        db.settings_set(setting, new_status)

        formatted_setting = setting.replace("_", " ").title()
        await query.answer(
            text=f"{formatted_setting} turned {'ON' if new_status else 'OFF'}."
        )

        settings = db.settings_get_all()
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{s.replace('_', ' ').title()}: {'ON' if v else 'OFF'}",
                    callback_data=f"settings_toggle_{s}"
                )
            ]
            for s, v in settings.items()
        ]
        keyboard.append(
            [
                InlineKeyboardButton("Reset Clicks", callback_data="question:clicks_reset")
            ]
        )

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
    except Exception as e:
        await query.answer(
        text=f"Error: {e}",
        show_alert=True
        )