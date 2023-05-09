from django.contrib.auth.models import BaseUserManager
from django.db import models

from django.utils import timezone
from django.contrib.auth import _get_backends


class RoyaltyManager(BaseUserManager):
    """Define a model manager for Royalty model with no username field."""

    use_in_migrations = True

    def get_by_natural_key(self, email):
        return self.select_related(
            'royaltyprofile').get(username=email)
