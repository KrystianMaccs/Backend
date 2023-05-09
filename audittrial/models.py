from django.db import models
from accounts.models import Artist
from royalty.models import Royalty


class Audittrial(models.Model):
    artist = models.ForeignKey(Artist, null=True, on_delete=models.SET_NULL)
    royalty = models.ForeignKey(Royalty, null=True, on_delete=models.SET_NULL)
    changed = models.CharField(max_length=100)
    action = models.CharField(max_length=25)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
