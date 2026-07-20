import re

from django.core.exceptions import ValidationError
from django.utils import timezone

from .decorators import doc
from reviews.constants import (
    FORBIDDEN_USERNAME,
    USERNAME_FIELD_LIMIT,
    USERNAME_CHARS
)


@doc(f"Запрещает использовать '{FORBIDDEN_USERNAME}' как username.")
def validate_username_not_me(value):
    if value == FORBIDDEN_USERNAME:
        raise ValidationError(
            f'Имя пользователя "{FORBIDDEN_USERNAME}" запрещено.'
        )


def validate_username_lenght(value):
    """Проверяет что длина username не больше 150"""
    if len(value) > USERNAME_FIELD_LIMIT:
        raise ValidationError(
            'Имя пользователя не может быть длиннее 150 символов.'
        )


def validate_username_chars(value):
    """Проверяет допустимые символы в username."""
    if not re.match(USERNAME_CHARS, value):
        raise ValidationError(
            'Username содержит недопустимые символы.'
        )


def validate_year(value):
    """Проверяет, что год не больше текущего."""
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            f'Год выпуска {value} не может быть больше текущего {current_year}'
        )
    return value
