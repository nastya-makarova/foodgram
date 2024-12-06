import random
import string

from foodgram.constants import MAX_LENGTH_SHORT_LINK


characters = string.ascii_letters + string.digits


def get_short_url(length=MAX_LENGTH_SHORT_LINK, characters=characters):
    """Метод генерирует короткую ссылку."""
    short_url_part = "".join(random.choice(characters) for _ in range(length))
    return short_url_part

