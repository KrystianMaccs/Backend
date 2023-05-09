import uuid
from django.db import models

from .managers import RoyaltyManager


class Royalty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    phone = models.CharField(max_length=15)
    last_authenticated = models.DateTimeField(null=True)
    last_updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def has_perms(self, perms):
        return False

    def has_perm(self, perm):
        return False

    objects = RoyaltyManager()

    def __str__(self):
        return self.username


class RoyaltyProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    royalty = models.OneToOneField(Royalty, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=45, blank=True, null=True)
    last_name = models.CharField(max_length=45, blank=True, null=True)
    other_names = models.CharField(max_length=45, blank=True, null=True)
    bio = models.CharField(max_length=100)
    account_number = models.CharField(max_length=19, blank=True, null=True)
    recipient_code = models.CharField(max_length=25, blank=True, null=True)
    bank_name = models.CharField(max_length=75, blank=True, null=True)
    bank_code = models.CharField(max_length=10, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name} {self.other_names}'

    def __str__(self):
        return self.get_full_name
