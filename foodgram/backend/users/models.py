"""Модели приложения users."""

from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_LEN_EMAIL = 254


class User(AbstractUser):
    """Модель пользователя сполем аватара и аутентификацией по email."""

    email = models.EmailField(
        verbose_name='email address',
        max_length=MAX_LEN_EMAIL,
        unique=True,
        help_text='Required. Enter a valid email address.'
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        default='',
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        """Мета-настройки модели пользователя."""

        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Возвращает строковое представление пользователя."""
        return self.username
