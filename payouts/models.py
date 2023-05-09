import uuid
from django.db import models
from django.contrib.auth import get_user_model

from accounts.models import Artist
from royalty.models import Royalty
from songs.models import Song, RoyaltySplit

User = get_user_model()

CHARGE_CHOICES = (
    ('PERCENTAGE', 'PERCENTAGE'),
    ('FLAT', 'FLAT')
)


class Charge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=75)
    description = models.CharField(max_length=100, null=True, blank=True)
    amount = models.FloatField()
    charge_type = models.CharField(choices=CHARGE_CHOICES, max_length=15)
    max_fee = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PayoutDue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    due_date = models.DateField(unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # def __repr__(self) -> str:
    #     return self.due_date

    def __str__(self):
        return str(self.due_date)


class Payout(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    confirm_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    payment_approved = models.BooleanField(default=False)
    pay_due: PayoutDue = models.ForeignKey(
        PayoutDue, null=True, on_delete=models.PROTECT)
    amount = models.FloatField(null=True, blank=True)
    approval_timestamp = models.DateTimeField(null=True)
    song_tracked_count = models.IntegerField(default=0)
    triggered = models.BooleanField(default=False)
    last_triggered = models.DateTimeField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pay_due)


class SongSales(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    song = models.ForeignKey(Song, on_delete=models.PROTECT)
    revenue = models.FloatField(default=0)
    deduction = models.FloatField(default=0)
    played_count = models.IntegerField(default=0)
    pay_due = models.ForeignKey(
        PayoutDue, null=True, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)


class ArtistPayout(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artist = models.ForeignKey(Artist, on_delete=models.PROTECT)
    approved_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    net_profit = models.FloatField(default=0)
    gross_profit = models.FloatField(default=0)
    total_deduction = models.FloatField(default=0)
    royalty_cut = models.FloatField(default=0)
    paid = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    is_processing = models.BooleanField(default=False)
    transaction_id = models.CharField(
        max_length=50, null=True, blank=True, unique=True)
    transaction_reference = models.CharField(
        max_length=25, null=True, blank=True)
    pay_due = models.ForeignKey(
        PayoutDue, null=True, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)


class RoyaltyPayout(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    royalty = models.ForeignKey(Royalty, on_delete=models.PROTECT)
    royalty_split = models.ManyToManyField(
        RoyaltySplit, blank=True)
    approved_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    amount = models.FloatField(null=True)
    deduction = models.FloatField(default=0)
    is_processing = models.BooleanField(default=False)
    transaction_id = models.CharField(
        max_length=25, null=True, blank=True, unique=True)
    pay_due = models.ForeignKey(
        PayoutDue, null=True, on_delete=models.PROTECT)
    paid = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class PayoutHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payout = models.OneToOneField(Payout, on_delete=models.PROTECT)
    total_paid = models.FloatField(default=0)
    paid_artists = models.IntegerField(default=0)
    paid_artist_royalty = models.IntegerField(default=0)
    gross = models.FloatField(default=0)
    artists_count = models.IntegerField(default=0)
    royalty_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
