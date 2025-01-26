import media, random, socket


def escape_markdown(text):
    characters_to_escape = ['*', '_', '`']
    for char in characters_to_escape:
        text = text.replace(char, '\\' + char)
    return text


def format_seconds(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    if minutes > 0:
        return f"{minutes} minutes and {remaining_seconds:.0f} seconds"
    else:
        return f"{remaining_seconds:.3f} secconds"


def is_local():
    ip = socket.gethostbyname(socket.gethostname())
    return ip.startswith("127.") or ip.startswith("192.168.") or ip == "localhost"


def random_button_time():
    time = random.randint(3600, 86400)
    return time


def random_logo():
    random_logo = random.choice(media.logos)
    return random_logo
