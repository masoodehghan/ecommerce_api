from rest_framework.permissions import BasePermission


class IsCartOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.cart.user == request.user

    def has_permission(self, request, view):
        return request.user.is_authenticated
