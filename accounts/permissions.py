from django.contrib.auth import get_user_model
from rest_framework import permissions

from .models import Artist

User = get_user_model()


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, User)

    def has_object_permission(self, request, view, obj):
        return isinstance(request.user, User)


class IsArtistOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, Artist)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user == obj


class IsArtist(permissions.BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, Artist)

    def has_object_permission(self, request, view, obj):
        return request.user == obj


class IsArtistOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, Artist)

    def has_object_permission(self, request, view, obj):
        return request.user == obj.artist


class IsStaffOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class IsStafpfOrReadOnly(permissions.BasePermission):
    def has_ermission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return isinstance(request.user, Artist)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user == obj
