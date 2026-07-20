import random
import string

from yacut.models import URLMap

MAX_CUSTOM_ID_LENGTH = 16
LENGTH_SHORT_ID = 6
RESERVED_SHORT_ID = 'files'
INVALID_CUSTOM_ID = "Указано недопустимое имя для короткой ссылки"
DUPLICATE_CUSTOM_ID = "Предложенный вариант короткой ссылки уже существует."


def get_unique_short_id(length=LENGTH_SHORT_ID):
    chars = string.ascii_letters + string.digits
    while True:
        short = ''.join(random.choice(chars) for _ in range(length))
        if not URLMap.query.filter_by(short=short).first():
            return short


def is_custom_id_valid(custom_id):
    if len(custom_id) > MAX_CUSTOM_ID_LENGTH:
        return False, INVALID_CUSTOM_ID

    for char in custom_id:
        if char not in string.ascii_letters + string.digits:
            return False, INVALID_CUSTOM_ID

    if custom_id.lower() == RESERVED_SHORT_ID:
        return False, DUPLICATE_CUSTOM_ID

    if URLMap.query.filter_by(short=custom_id).first():
        return False, DUPLICATE_CUSTOM_ID

    return True, None
