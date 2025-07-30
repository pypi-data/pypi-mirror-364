import random
from pathlib import Path
from string import ascii_letters


def random_str(k=8):
    return ''.join(random.sample(ascii_letters, k))


def user_desktop_dir():
    return Path.home() / "Desktop"
