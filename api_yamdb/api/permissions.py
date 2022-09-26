from rest_framework import permissions

DEFAULT_PERMISSION_MESSAGE = 'Нет прав доступа'


class IsAdminOnly(permissions.BasePermission):
    message = 'Действие доступно только пользователю с ролью администратор!'

    def has_permission(self, request, view):
        return request.user.is_admin


class IsAdminUserOrReadOnly(permissions.BasePermission):
    message = DEFAULT_PERMISSION_MESSAGE

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and request.user.is_admin
        )


class IsStaffOrAuthorOrReadOnly(permissions.BasePermission):
    message = DEFAULT_PERMISSION_MESSAGE

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
