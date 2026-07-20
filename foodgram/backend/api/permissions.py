"""Права доступа для API."""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Права доступа: автор или только чтение."""

    def has_object_permission(self, request, view, obj):
        """Проверяет разрешение на уровне конкретного объекта."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff
