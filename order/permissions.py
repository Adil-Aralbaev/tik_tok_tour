from rest_framework.permissions import BasePermission


class IsAdminOrManagerOrCustomer(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(obj.user == request.user)
