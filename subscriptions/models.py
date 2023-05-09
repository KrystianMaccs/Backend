import uuid
from django.db import models

from accounts.models import Artist


class Package(models.Model):
    GO_DISTRO = 'GO_DISTRO'
    GO_MONITOR = 'GO_MONITOR'
    FEATURES = (
        (GO_DISTRO, 'Go Distro'),
        (GO_MONITOR, 'Go Monitor'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=35)
    description = models.CharField(max_length=225)
    tracks_count = models.IntegerField(default=0)
    eta_months = models.IntegerField(default=0)
    eta_years = models.IntegerField(default=0)
    sku_id = models.CharField(max_length=15, null=True, blank=True)
    eveara_id = models.IntegerField(default=0, null=True)
    feature = models.CharField(
        max_length=50, choices=FEATURES, default=GO_DISTRO)
    price = models.FloatField()
    last_updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class ArtistSubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    package: Package = models.ForeignKey(Package, on_delete=models.CASCADE)
    songs_added = models.IntegerField(default=0)
    expired = models.BooleanField(default=False)
    activated = models.BooleanField(default=False)
    provisioned = models.BooleanField(default=False)
    eveara_id = models.IntegerField(default=0, null=True)
    last_renewed = models.DateTimeField(null=True, blank=True)
    expired_timestamp = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class SubscriptionTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_successful = models.BooleanField(default=False)
    payment_gateway = models.CharField(max_length=30, default='STRIPE')
    subscription = models.ForeignKey(
        ArtistSubscription, on_delete=models.CASCADE)
    transaction_reference = models.CharField(max_length=150, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)


