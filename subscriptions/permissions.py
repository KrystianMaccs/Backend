from rest_framework import permissions

from django.contrib.auth import get_user_model


User = get_user_model()


class HasPackagePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(user, User):
            return user.has_perm('Can add package')

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(user, User):
            return user.has_perm('Can add package')

        return False
