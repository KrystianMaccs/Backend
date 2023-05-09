from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class CanPayout(permissions.BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, User)

    def has_object_permission(self, request, view, obj):
        return isinstance(request.user, User)
