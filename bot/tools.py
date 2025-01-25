import media, random


def escape_markdown(text):
    characters_to_escape = ['*', '_', '`']
    for char in characters_to_escape:
        text = text.replace(char, '\\' + char)
    return text


def random_button_time():
    time = random.randint(3600, 86400)
    return time


def random_logo():
    random_logo = random.choice(media.logos)
    return random_logo
