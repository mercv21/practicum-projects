from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Доступ только для администраторов."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Администратор может всё, остальные только читать.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and (request.user.is_admin)
            )
        )


class IsAdminOrModeratorOrReadOnly(permissions.BasePermission):
    """
    Модератор и администратор могут редактировать и удалять.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
