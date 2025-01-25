from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import time, random
from datetime import datetime

from bot import db, settings, tools
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
            settings.RESTART_TIME = datetime.now().timestamp()
            settings.BUTTON_TIME = tools.random_button_time()
            job_queue.run_once(
                button_send,
                settings.BUTTON_TIME,
                chat_id=settings.TG_CHANNEL_ID,
                name="Click Me",
            )



async def button_send(context: ContextTypes.DEFAULT_TYPE):
    context.bot_data["first_user_clicked"] = False

    previous_click_me_id = context.bot_data.get('click_me_id')
    previous_clicked_id = context.bot_data.get('clicked_id')

    if previous_click_me_id:
        try:
            await context.bot.delete_message(chat_id=settings.TG_CHANNEL_ID, message_id=previous_click_me_id)
            await context.bot.delete_message(chat_id=settings.TG_CHANNEL_ID, message_id=previous_clicked_id)
        except Exception:
            pass

    current_button_data = str(random.randint(1, 100000000))
    context.bot_data["current_button_data"] = f"click_button:{current_button_data}"

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Click Me!", callback_data=context.bot_data["current_button_data"])]]
    )
    click_me = await context.bot.send_photo(
        photo=tools.random_logo(),
        chat_id=settings.TG_CHANNEL_ID,
        reply_markup=keyboard,
    )

    context.bot_data["button_generation_timestamp"] = time.time()
    context.bot_data['click_me_id'] = click_me.message_id