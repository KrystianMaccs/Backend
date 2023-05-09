from django.contrib import admin
from .models import ArtistSubscription, SubscriptionTransaction, Package

admin.site.register(Package)
admin.site.register(ArtistSubscription)
admin.site.register(SubscriptionTransaction)
