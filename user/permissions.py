from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        if view.__class__.__name__ == 'ProfileView':
            if not request.user.is_authenticated:
                return False

            return request.user == obj

        elif view.__class__.__name__ == 'AddressRetrieveView':
            return request.user == obj.user
