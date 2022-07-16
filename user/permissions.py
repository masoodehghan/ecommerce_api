from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        if view.__class__.__name__ == 'ProfileView':
            return request.user == obj
        else:
            return request.user == obj.user

    def has_permission(self, request, view):
        return request.user.is_authenticated
