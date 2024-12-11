from rest_framework import permissions


class UnauthorizedOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return True
        return request.user.is_staff