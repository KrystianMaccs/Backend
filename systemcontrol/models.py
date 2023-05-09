import uuid
from django.db import models


class SystemDefault(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=45)
    description = models.CharField(max_length=75)
    nkey = models.CharField(max_length=45)
    nvalue = models.CharField(max_length=75)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Settings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    eveara_user_id = models.CharField(max_length=75, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Outlet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    storeId = models.CharField(max_length=15)
    storeName = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)


class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country_name = models.CharField(max_length=45)
    country_code = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)


class SupportedMonitor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
