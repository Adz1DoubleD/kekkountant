from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import random, requests
from pyfiglet import Figlet
from gtts import gTTS

from bot import db, settings, tools


async def ascii(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input_text = " ".join(context.args).upper()
    if input_text == "":
        await update.message.reply_text(
            f"Please follow the command with the word you want to use",
        parse_mode="Markdown",
        )
    else:
        words = input_text.split()
        input_text = "\n".join(words)
        custom_fig = Figlet(font="slant")
        ascii_art = custom_fig.renderText(input_text)
        await update.message.reply_text(
            f"*{settings.PROJECT_NAME} ASCII Art*\n\n"
            f"Best viewed on PC full screen.\n\n`{ascii_art}`",
        parse_mode="Markdown",
        )


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not settings.CA:
        await update.message.reply_photo(
        photo = tools.random_logo(),
        caption=
            f"*{settings.PROJECT_NAME} CA*\n\nComing Soon!\n\n",
        parse_mode="Markdown"
        )
        return

    await update.message.reply_photo(
        photo = tools.random_logo(),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"Buy On Uniswap", url=f"https://app.uniswap.org/#/swap?chain={settings.CHAIN}&outputCurrency={settings.CA}"
                    )
                ]
            ]
        ),
    )


async def ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not settings.CA:
        await update.message.reply_photo(
        photo = tools.random_logo(),
        caption=
            f"*{settings.PROJECT_NAME} CA*\n\nComing Soon!\n\n",
        parse_mode="Markdown"
        )
        return

    await update.message.reply_photo(
        photo = tools.random_logo(),
        caption=
            f"*{settings.PROJECT_NAME} CA* \n\n`{settings.CA}`\n\n",
        parse_mode="Markdown"
    )


async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not settings.CA:
        await update.message.reply_photo(
        photo = tools.random_logo(),
        caption =
            f"*{settings.PROJECT_NAME} Chart*\n\nComing Soon!\n\n",
        parse_mode="Markdown"
        )
        return
    await update.message.reply_photo(
        photo = tools.random_logo(),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"📈 Chart", url=f"{settings.CHART_LINK}"
                    )
                ]
            ]
        ),
    )


async def coinflip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = user.username or f"{user.first_name} {user.last_name}"
    choose = ["Heads", "Tails"]
    choice = random.choice(choose)
    await update.message.reply_photo(
        photo = tools.random_logo(),
        caption =
            f"*{settings.PROJECT_NAME} Coin Flip*\n\n{tools.escape_markdown(user_info)} flipped {choice}\n\n",
        parse_mode="Markdown"
)


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo = tools.random_logo(),
        caption=(
            f"*{settings.PROJECT_NAME} Daily Tasks*\n\n"
            "Vote for us on the following links\n"
            f"- [Dexscreener](https://dexscreener.com/{settings.CHAIN}/{settings.CA})\n"
            f"- [Dextools](https://www.dextools.io/app/en/{settings.CHAIN}/pair-explorer/{settings.CA})\n"
            f"- [CoinGecko](https://www.coingecko.com/en/coins/{settings.TICKER.lower()})\n"
            f"- [Coin Market Cap](https://coinmarketcap.com/currencies/{settings.PROJECT_NAME})\n\n"
            "Like and RT everything on the link below\n"
            f"- [{settings.PROJECT_NAME} Twitter Search](https://twitter.com/search?q=%23{settings.PROJECT_NAME.upper()}&src=typed_query)\n\n"
            f"Post at least 5 tweets a day and share them here with the link below\n"
            f"- [Create Tweets with {settings.PROJECT_NAME} tags](http://twitter.com/intent/tweet?text=%0A%0A%0A@{settings.TWITTER}%20${settings.PROJECT_NAME.upper()}&url=%0A{settings.WEBSITE}&hashtags={settings.PROJECT_NAME.upper()}%2CDEFIDOGS)"
        ),
        parse_mode="Markdown"
    )

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke_response = requests.get("https://v2.jokeapi.dev/joke/Any?safe-mode")
    joke = joke_response.json()
    if joke["type"] == "single":
        await update.message.reply_photo(
        photo = tools.random_logo(),
        caption =
            f'{settings.PROJECT_NAME} Joke\n\n'
            f'{joke["joke"]}\n\n',
        parse_mode="Markdown"
        )
    else:
        await update.message.reply_photo(
        photo = tools.random_logo(),
        caption =
            f'{settings.PROJECT_NAME} Joke\n\n'
            f'{joke["setup"]}\n\n{joke["delivery"]}\n\n',
        parse_mode="Markdown"
        )


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    board = db.clicks_get_leaderboard()
    click_counts_total = db.clicks_get_total()
    fastest_user, fastest_time = db.clicks_fastest_time()
    streak_user, streak_value = db.clicks_check_highest_streak()
    message = (
        f"*Fastest player Leaderboard*\n\n"
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


async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text('Please follow the command with a maximum number for the roll')
        return
    else:
        max_number_str = context.args[0]
        if not max_number_str.isdigit():
            await update.message.reply_text('Please follow the command with a maximum number for the roll')

        max_number = int(max_number_str)
        if max_number < 2:
            await update.message.reply_text('Please follow the command with a maximum number for the roll')
            return
        
        user = update.effective_user
        user_info = user.username or f"{user.first_name} {user.last_name}"
        max_number = int(context.args[0])
        result = random.randint(1, max_number)
        await update.message.reply_photo(
        photo = tools.random_logo(),
        caption=
            f'*{settings.PROJECT_NAME} Number Roll*\n\n{tools.escape_markdown(user_info)} rolled {result}\n\nBetween 1 and {max_number}\n\n',
        parse_mode="Markdown",)


async def say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide some words to convert to speech.")
        return
    voice_note = gTTS(" ".join(context.args), lang='en', slow=False)
    voice_note.save(f"media/{settings.PROJECT_NAME}-voicenote.mp3")
    await update.message.reply_audio(audio=open(f"media/{settings.PROJECT_NAME}-voicenote.mp3", "rb"))


async def twitter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo = tools.random_logo(),
        reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=f"@{settings.TWITTER}",
                                url=f"https://twitter.com/{settings.TWITTER}",
                            )
                        ],
                    ]
                ),
            )


async def website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo = tools.random_logo(),
        reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=f"{settings.WEBSITE}",
                                url=f"https://{settings.WEBSITE}",
                            )
                        ],
                    ]
                ),
            )