import uuid
from django.db import models

from accounts.models import Artist
from sso.tasks import secret_key_gen


class IdentityApp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=75)
    description = models.CharField(max_length=150, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    
    redirect_url = models.URLField()
    private_key = models.CharField(max_length=128, default=secret_key_gen, db_index=True)
    public_key = models.CharField(max_length=128, default=secret_key_gen, db_index=True)

    last_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class AppAuthLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    identity_app = models.ForeignKey(IdentityApp, on_delete=models.CASCADE)
    artist: Artist = models.ForeignKey(Artist, on_delete=models.CASCADE)

    accessToken = models.CharField(max_length=255, db_index=True)
    client_ip = models.CharField(max_length=15)
    client_user_agent = models.CharField(max_length=255)

    app_ip = models.CharField(max_length=15, null=True)
    approval_request_count = models.IntegerField(default=0)
    app_user_agent = models.CharField(max_length=255, null=True)
    approval_request_timestamp = models.DateTimeField(null=True)

    last_request_timestamp = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
