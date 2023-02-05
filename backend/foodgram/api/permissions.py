from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    message = 'Нет прав для внесения изменений'

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (
                request.method in SAFE_METHODS
                or obj.author == request.user
            )
        return request.method in SAFE_METHODS


class IsAdmin(BasePermission):
    message = 'Такие права имеет только админ.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()