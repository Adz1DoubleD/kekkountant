from telegram import Update
from telegram.ext import CallbackContext, ContextTypes

from datetime import datetime, timedelta

from bot import callbacks, db, settings, tools


async def click_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in settings.TG_ADMIN_ID:
        await callbacks.button_send(context)


async def leaderboard(update: Update, context: CallbackContext):
    board = db.clicks_get_leaderboard()
    click_counts_total = db.clicks_get_total()
    fastest_user, fastest_time = db.clicks_fastest_time()
    streak_user, streak_value = db.clicks_check_highest_streak()
    year = datetime.now().year
    message = (
        f"*Fastest player {year} Leaderboard*\n\n"
        f"{tools.escape_markdown(board)}\n"
        f"Total clicks: *{click_counts_total}*\n"
        f"\nFastest click:\n"
        f"{fastest_time:,.3f} seconds\n"
        f"by @{tools.escape_markdown(fastest_user)}\n\n"
        f"@{tools.escape_markdown(streak_user)} clicked the button last and is on a *{streak_value}* click streak!"
    )

    await update.message.reply_text(
        message,
        parse_mode="Markdown"
    )


async def me(update: Update, context: CallbackContext):
    user = update.effective_user
    user_info = user.username or f"{user.first_name} {user.last_name}" or user.first_name
    info = db.clicks_get_by_name(user_info)
    
    await update.message.reply_text(
        f"{user_info}\n\n"
        f"Total clicks: {info[0]}\n"
        f"Fastest Time: {info[1]} seconds\n"
        f"Current Streak: {info[2]}\n",
        parse_mode="Markdown"
    )


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