"""Регистрация модели пользователя в админке."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Кастомная настройка отображения пользователя в админке."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name'
    )
    search_fields = (
        'username',
        'email',
    )
