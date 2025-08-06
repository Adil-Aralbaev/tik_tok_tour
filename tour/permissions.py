from rest_framework import permissions


class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return bool(request.user.is_staff or request.user.role == 'Author')
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user.is_staff or obj.author == request.user)


class IsAdminOrManagerOrAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user.is_staff or request.user.role == 'Manager')

    def has_object_permission(self, request, view, obj):
        return bool(obj.tour.author == request.user)



