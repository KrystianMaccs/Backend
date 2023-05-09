from django.contrib.auth.models import BaseUserManager
from django.db import models

from django.utils import timezone
from django.contrib.auth import _get_backends


class ArtistManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_artist(self, password, email, **extra_fields):
        """
        Create and save an Artist with the given email and password.
        """

        if email is None:
            raise ValueError(f'The given value email must be set')

        email = self.normalize_email(email).lower()

        user = self.model(email=email, **extra_fields)

        if user.stage_name is None:
            user.stage_name = extra_fields.get(
                'first_name', '') + ' ' + extra_fields.get('last_name', '')

        user.set_password(self.make_random_password())
        user.is_active = False
        user.is_verified = False
        user.save(using=self._db)
        return user

    def create_artist(self, password=None, email=None, **extra_fields):
        return self._create_artist(password, email, **extra_fields)

    def get_by_email(self, email):
        artist = self.get_queryset().filter(email=email)
        if artist.count() > 0:
            return artist.distinct()
        return None

    def get_by_natural_key(self, email):
        return self.select_related(
            'userphoto').get(email=email)
