from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.is_admin()
        return False


class IsAuthorAdminModeratorOrReadOnly(BasePermission):
    message = 'Нет прав для внесения изменений'

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (
                request.method in SAFE_METHODS
                or obj.author == request.user
                or request.user.is_admin()
                or request.user.is_moderator()
            )
        return request.method in SAFE_METHODS


class IsAdmin(BasePermission):
    message = 'Такие права имеет только админ.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()