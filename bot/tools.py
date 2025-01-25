import os, random


def escape_markdown(text):
    characters_to_escape = ['*', '_', '`']
    for char in characters_to_escape:
        text = text.replace(char, '\\' + char)
    return text


def random_button_time():
    time = random.randint(3600, 86400)
    return time


def random_logo():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    media_path = os.path.join(base_dir, "media")
    files = [f for f in os.listdir(media_path) if os.path.isfile(os.path.join(media_path, f))]
    random_file = random.choice(files)
    random_logo_path = f"media/{random_file}"
    return random_logo_path
