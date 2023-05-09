from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from django_q.tasks import async_task

from .models import (Artist, UserPhoto, ArtistStorage,
                     BankAccount, StaffProfile, ArtistMeta)
from songs.models import Album, Label

from utils.helper import value_not_empty 


User = get_user_model()


def create_user_photo(instance):
    photo = UserPhoto()
    if isinstance(instance, User):
        profile = StaffProfile()
        profile.user = instance

        photo.user = instance
        photo.artist = None

        profile.save()

    elif isinstance(instance, Artist):
        photo = UserPhoto()
        photo.artist = instance
        photo.user = None

    photo.save()


@receiver(post_save, sender=Artist)
def new_artist_receiver(sender, **kwargs):
    instance = kwargs['instance']
    if kwargs['created']:
        create_artist_meta(instance)

    elif instance.is_active and value_not_empty(instance.stage_name):
        # async_task('accounts.signals.get_or_create_label', instance)

        if instance.artistmeta.eveara_artist_id is None: 
            async_task('utils.api.eveara.create_artist', instance)


def create_artist_meta(instance):
    ArtistMeta.objects.get_or_create(artist=instance)
    Album.objects.get_or_create(
        title='General',
        description='Collections of songs without category or album',
        artist=instance
    )

    create_user_photo(instance)
    ArtistStorage.objects.create(artist=instance)
    BankAccount.objects.create(artist=instance)

    if instance.artistmeta.eveara_artist_id is None and value_not_empty(instance.stage_name):
        async_task('utils.api.eveara.create_artist', instance)


def get_or_create_label(artist):
    labels = Label.objects.filter(artist=artist)
    print("Create Label ", artist.stage_name)

    if labels.exists():
        label = Label.objects.get_or_create(
            artist=artist,
            title=artist.stage_name
        )

        album = Album.objects.filter(artist=artist)
        album.order_by('timestamp')
        if album.exists():
            album = album.first()
            album.label = label
            album.save()


@receiver(post_save, sender=User)
def new_user_receiver(sender, **kwargs):
    instance = kwargs['instance']
    if kwargs['created']:
        async_task('accounts.signals.create_user_photo', instance)
