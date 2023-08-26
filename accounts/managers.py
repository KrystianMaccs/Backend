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


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)