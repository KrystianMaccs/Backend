from django.db import models

import uuid


class Plan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=45)
    description = models.CharField(max_length=255)
    expiry_month = models.IntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Advert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(Plan, null=True, on_delete=models.SET_NULL)
    details = models.TextField(blank=True)
    file_type = models.CharField(max_length=15)
    file = models.FileField(upload_to='files/adverts')
    visits = models.IntegerField(default=0)
    short_text = models.CharField(max_length=155, null=True, blank=True)
    link = models.URLField(null=True,
                           blank=True, max_length=200)
    last_updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.short_text
