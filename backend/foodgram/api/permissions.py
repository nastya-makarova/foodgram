from rest_framework import permissions


class UnauthorizedOrAdmin(permissions.BasePermission):
    """
    Разрешение, которое позволяет доступ неавторизованным
    пользователям или администраторам.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return True
        return request.user.is_staff


class RecipePermisssion(permissions.BasePermission):
    """
    Доступ разрешен для безопасных методов; аутентифицированным пользователям;
    администраторам.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user == obj.author)
            or request.user.is_staff
        )
