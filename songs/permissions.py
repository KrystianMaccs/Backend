from rest_framework import permissions

from accounts.models import Artist


class IsAlbumOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.artist


class IsAritstVerified(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(user, Artist):
            return True
        return False


class IsSongOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(user, Artist):
            return obj.artist == user

        return False


class IsSplitOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(user, Artist):
            return obj.song.artist_id == user.id

        return False


class IsObjOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(user, Artist):
            return obj.artist == user

        return False
