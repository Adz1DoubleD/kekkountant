from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import io
import random
import requests
from datetime import datetime
from pyfiglet import Figlet
from gtts import gTTS

from bot import constants
from utils import tools
from services import get_dbmanager

db = get_dbmanager()


async def ascii(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input_text = " ".join(context.args).upper()
    if input_text == "":
        await update.message.reply_text(
            "Please follow the command with the word you want to use",
            parse_mode="Markdown",
        )
    else:
        words = input_text.split()
        input_text = "\n".join(words)
        custom_fig = Figlet(font="slant")
        ascii_art = custom_fig.renderText(input_text)
        await update.message.reply_text(
            f"*{constants.PROJECT_NAME} ASCII Art*\n\n"
            f"Best viewed on PC full screen.\n\n`{ascii_art}`",
            parse_mode="Markdown",
        )


async def ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not constants.CA:
        await update.message.reply_photo(
            photo=tools.random_logo(),
            caption=f"*{constants.PROJECT_NAME} CA*\n\nComing Soon!\n\n",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_photo(
        photo=tools.random_logo(),
        caption=f"*{constants.PROJECT_NAME} CA* \n\n`{constants.CA}`\n\n",
        parse_mode="Markdown",
    )


async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not constants.CA:
        await update.message.reply_photo(
            photo=tools.random_logo(),
            caption=f"*{constants.PROJECT_NAME} Chart*\n\nComing Soon!\n\n",
            parse_mode="Markdown",
        )
        return
    await update.message.reply_photo(
        photo=tools.random_logo(),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="📈 Chart", url=f"{constants.CHART_LINK}")]]
        ),
    )


async def coinflip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = user.username or f"{user.first_name} {user.last_name}"
    choose = ["Heads", "Tails"]
    choice = random.choice(choose)
    await update.message.reply_photo(
        photo=tools.random_logo(),
        caption=f"*{constants.PROJECT_NAME} Coin Flip*\n\n{tools.escape_markdown(user_info)} flipped {choice}\n\n",
        parse_mode="Markdown",
    )


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.random_logo(),
        caption=(
            f"*{constants.PROJECT_NAME} Daily Tasks*\n\n"
            "Vote for us on the following links\n"
            f"- [Dexscreener](https://dexscreener.com/{constants.CHAIN}/{constants.CA})\n"
            f"- [Dextools](https://www.dextools.io/app/en/{constants.CHAIN}/pair-explorer/{constants.CA})\n"
            f"- [CoinGecko](https://www.coingecko.com/en/coins/{constants.TICKER.lower()})\n"
            f"- [Coin Market Cap](https://coinmarketcap.com/currencies/{constants.PROJECT_NAME})\n\n"
            "Like and RT everything on the link below\n"
            f"- [{constants.PROJECT_NAME} Twitter Search](https://twitter.com/search?q=%23{constants.PROJECT_NAME.upper()}&src=typed_query)\n\n"
            f"Post at least 5 tweets a day and share them here with the link below\n"
            f"- [Create Tweets with {constants.PROJECT_NAME} tags](http://twitter.com/intent/tweet?text=%0A%0A%0A@{constants.TWITTER}%20${constants.PROJECT_NAME.upper()}&url=%0A{constants.WEBSITE}&hashtags={constants.PROJECT_NAME.upper()}%2CDEFIDOGS)"
        ),
        parse_mode="Markdown",
    )


async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.random_logo(),
        caption=f"*{constants.PROJECT_NAME} Facts*\n\n{random.choice(constants.FACTS)}",
        parse_mode="Markdown",
    )


async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke_response = requests.get("https://v2.jokeapi.dev/joke/Any?safe-mode")
    joke = joke_response.json()
    if joke["type"] == "single":
        await update.message.reply_photo(
            photo=tools.random_logo(),
            caption=f"{constants.PROJECT_NAME} Joke\n\n{joke['joke']}\n\n",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_photo(
            photo=tools.random_logo(),
            caption=f"{constants.PROJECT_NAME} Joke\n\n"
            f"{joke['setup']}\n\n{joke['delivery']}\n\n",
            parse_mode="Markdown",
        )


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    board = await db.get_leaderboard()
    click_counts_total = await db.get_total_clicks()
    fastest_user, fastest_time = await db.get_fastest_time()
    streak_user, streak_value = await db.check_highest_streak()
    formatted_fastest_time = tools.format_seconds(fastest_time)

    message = (
        f"*Fastest player Leaderboard*\n\n"
        f"{tools.escape_markdown(board)}\n"
        f"Total clicks: *{click_counts_total}*\n\n"
        f"Fastest click:\n"
        f"{formatted_fastest_time}\n"
        f"by @{tools.escape_markdown(fastest_user)}\n\n"
        f"@{tools.escape_markdown(streak_user)} clicked the button last and is on a *{streak_value}* click streak!"
    )

    await update.message.reply_text(message, parse_mode="Markdown")


async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = (
        user.username or f"{user.first_name} {user.last_name}" or user.first_name
    )
    info = await db.get_by_name(user_info)

    await update.message.reply_text(
        f"{user_info}\n\n"
        f"Total clicks: {info[0]}\n"
        f"Fastest Time: {info[1]} seconds\n"
        f"Current Streak: {info[2]}\n",
        parse_mode="Markdown",
    )


async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Please follow the command with a maximum number for the roll"
        )
        return
    else:
        max_number_str = context.args[0]
        if not max_number_str.isdigit():
            await update.message.reply_text(
                "Please follow the command with a maximum number for the roll"
            )

        max_number = int(max_number_str)
        if max_number < 2:
            await update.message.reply_text(
                "Please follow the command with a maximum number for the roll"
            )
            return

        user = update.effective_user
        user_info = user.username or f"{user.first_name} {user.last_name}"
        max_number = int(context.args[0])
        result = random.randint(1, max_number)
        await update.message.reply_photo(
            photo=tools.random_logo(),
            caption=f"*{constants.PROJECT_NAME} Number Roll*\n\n{tools.escape_markdown(user_info)} rolled {result}\n\nBetween 1 and {max_number}\n\n",
            parse_mode="Markdown",
        )


async def say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Please provide some words to convert to speech."
        )
        return

    text = " ".join(context.args)
    voice_note = gTTS(text, lang="en", slow=False)

    audio_buffer = io.BytesIO()
    voice_note.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    await update.message.reply_audio(
        audio=audio_buffer, filename=f"{constants.PROJECT_NAME}-voicenote.mp3"
    )


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    url = f"https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all/{now.month}/{now.day}"

    response = requests.get(url)
    data = response.json()

    if (
        "selected" in data
        and isinstance(data["selected"], list)
        and len(data["selected"]) > 0
    ):
        random_event = random.choice(data["selected"])

        event_text = random_event.get("text", "No description available.")
        year = random_event.get("year", "Unknown Year")

        event_pages = random_event.get("pages", [])
        wiki_url = (
            event_pages[0]["content_urls"]["desktop"]["page"]
            if event_pages
            else "No link available."
        )

        today_info = f"📅 *{year}*: {event_text}\n🔗 [Read more]({wiki_url})"

    today_info = "⚠️ No historical events found for today."
    await update.message.reply_photo(
        photo=tools.random_logo(),
        caption=f"*{constants.PROJECT_NAME} Today in history*\n\n{today_info}",
        parse_mode="Markdown",
    )


async def twitter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.random_logo(),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"@{constants.TWITTER}",
                        url=f"https://twitter.com/{constants.TWITTER}",
                    )
                ],
            ]
        ),
    )


async def website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.random_logo(),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{constants.WEBSITE}",
                        url=f"https://{constants.WEBSITE}",
                    )
                ],
            ]
        ),
    )


async def word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        word = " ".join(context.args).lower()
        if word == "":
            await update.message.reply_text(
                "Please use /word followed by the word you want to search"
            )
            return
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)
        data = response.json()

        definition = None
        audio_url = None

        if data and isinstance(data, list):
            meanings = data[0].get("meanings", [])
            if meanings:
                for meaning in meanings:
                    definitions = meaning.get("definitions", [])
                    if definitions:
                        definition = definitions[0].get("definition")
                        break

            phonetics = data[0].get("phonetics", [])
            if phonetics:
                first_phonetic = phonetics[0]
                audio_url = first_phonetic.get("audio")

        caption = f"*{constants.PROJECT_NAME} Dictionary*\n\n{word}:\n\n{definition}"
        keyboard_markup = None

        if audio_url:
            keyboard_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Pronunciation", url=f"{audio_url}")]]
            )

        await update.message.reply_photo(
            photo=tools.random_logo(),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=keyboard_markup,
        )
    except Exception:
        await update.message.reply_text("Word not found")


HANDLERS = [
    (func.__name__.split("_")[0], func, description)
    for func, description in [
        (ascii, "Create ASCII art"),
        (ca, "Contract Address"),
        (chart, "Chart link"),
        (coinflip, "Flip a coin"),
        (daily, "Daily tasks"),
        (fact, "Random fact"),
        (joke, "Random joke"),
        (leaderboard, "Click Me leaderboard"),
        (me, "My Click Me stats"),
        (roll, "Roll a number"),
        (say, "Text to speech"),
        (today_command, "Today in history"),
        (twitter, "Twiitter link"),
        (website, "Website link"),
        (word, "Dictionary"),
    ]
]
