from rest_framework import authentication
from django.contrib.auth import get_user_model
from .models import Artist


class CustomArtistBackend(authentication.BaseAuthentication):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(Artist.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = Artist._default_manager.get_by_natural_key(username.lower())
        except Artist.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            Artist().set_password(password)
        else:
            if user.check_password(password):
                return user
