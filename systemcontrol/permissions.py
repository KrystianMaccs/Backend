from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import permissions
from songs.models import Song
from subscriptions.models import ArtistSubscription, Package
from subscriptions.utils import get_artist_active_plan

from systemcontrol.utils import is_free_monitor

User = get_user_model()


class IsFreeOrActiveMonitorSub(permissions.BasePermission):

    def has_object_permission(self, request, view, obj: Song):
        can_request = is_free_monitor(obj.artist)

        if not can_request:
            now = timezone.now()
            song_sub: ArtistSubscription = obj.subscription
            can_request = not song_sub.expired and song_sub.activated and song_sub.expired_timestamp > now

        return can_request


class CanViewArtist(permissions.BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, User)

    def has_object_permission(self, request, view, obj):
        return isinstance(request.user, User)


class CanDeleteArtist(permissions.BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, User)

    def has_object_permission(self, request, view, obj):
        return isinstance(request.user, User)


class CanDisableArtist(permissions.BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, User)

    def has_object_permission(self, request, view, obj):
        return isinstance(request.user, User)
