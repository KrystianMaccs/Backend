from rest_framework import permissions
from .models import Royalty


class IsRoyalty(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(isinstance(request.user, Royalty))

    def has_object_permission(self, request, view, obj):
        return bool(isinstance(request.user, Royalty))


class IsRoyaltyOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user == obj


class IsProfileOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user == obj.royalty
