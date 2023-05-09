from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django_q.tasks import async_task
from accounts.models import Artist
from systemcontrol.utils import is_free_monitor

from utils.api.eveara.songs import delete_album

from .models import Song, Album, SongMeta, AlbumMeta, Label

from utils.song import upload_calculator
from utils.api.eveara import delete_song
from utils.helper import value_not_empty


def create_song_meta(instance):
    SongMeta.objects.get_or_create(song=instance)


def create_album_meta(instance):
    AlbumMeta.objects.get_or_create(album=instance)


def substract_file_size(instance):
    try:
        storage = instance.artist.artiststorage
        used = storage.used_space
        file_size = instance.file_size
        actual = upload_calculator(
            file_size) if file_size > 0 else upload_calculator(instance.file.size)

        pace = used - actual
        storage.used_space = pace
        storage.save()
    except Exception as e:
        print("Storage calculations failed ", e)


def delete_cover(instance):
    if instance.cover is not None:
        instance.cover.delete()


def delete_file_and_encoded(instance):
    substract_file_size(instance)
    instance.file.delete()
    if instance.encoded is not None:
        instance.encoded.delete()


@receiver(post_save, sender=Label)
def label_receiver(sender, **kwargs):
    instance = kwargs['instance']
    album = Album.objects.filter(artist_id=instance.artist_id)
    album = album.order_by('timestamp')

    if album.exists():
        album = album.first()
        if album.label is None:
            album.label = instance
            album.save()

    if value_not_empty(instance.title):
        async_task('utils.api.eveara.label', label=instance,
                   is_edit=not kwargs.get('created'))


@receiver(pre_delete, sender=Label)
def label_delete_receiver(sender, **kwargs):
    disseminate_label_id = kwargs['instance'].disseminate_label_id
    if disseminate_label_id is not None:
        async_task('utils.api.eveara.delete_label',
                   label_id=disseminate_label_id)


@receiver(post_save, sender=Song)
def new_song_receiver(sender, **kwargs):
    song: Song = kwargs['instance']

    if kwargs['created']:
        create_song_meta(song)

        if is_free_monitor(song.artist):
            async_task('utils.api.djm.create_track_fingerprint',
                       track=song, request=None)


@receiver(post_save, sender=Album)
def post_album_create(sender, **kwargs):
    instance = kwargs['instance']
    if kwargs['created']:
        create_album_meta(instance)

    else:
        album_meta = instance.albummeta
        eveara_id = album_meta.distribute_id
        if eveara_id is not None:
            async_task('utils.api.eveara.album_upload', album=instance,
                       subscription=None, is_edit=True)


@receiver(pre_delete, sender=Album)
def remove_album_files(sender, **kwargs):
    instance = kwargs['instance']
    delete_cover(instance)


@receiver(pre_delete, sender=Song)
def remove_song_files(sender, **kwargs):
    instance = kwargs['instance']
    delete_cover(instance)
    delete_file_and_encoded(instance)
    song_meta = instance.songmeta

    eveara_id = song_meta.disseminate_id
    if eveara_id is not None:
        try:
            delete_song(instance)
        except Exception as e:
            print('song delete error: ', e)


@receiver(pre_delete, sender=Album)
def remove_album(sender, **kwargs):
    instance = kwargs['instance']
    album_meta = instance.albummeta
    eveara_id = album_meta.distribute_id
    if eveara_id is not None:
        delete_album(eveara_id)
