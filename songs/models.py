import uuid
from django.db import models

from jsonfield import JSONField

from accounts.models import Artist
from royalty.models import Royalty
from subscriptions.models import ArtistSubscription
from utils.song import calculate_size
from utils.helper import redefinedFileName, redefinedSongFileName, resizeImage


class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    code = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AccessAvailability(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    code = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Label(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artist = models.ForeignKey(Artist, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=45)
    description = models.CharField(max_length=100, null=True, blank=True)
    disseminate_label_id = models.CharField(
        max_length=11, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Song(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=55)
    description = models.CharField(max_length=100)
    artist: Artist = models.ForeignKey(
        Artist, null=True, on_delete=models.CASCADE)
    file = models.FileField(upload_to=redefinedSongFileName)
    file_size = models.IntegerField(default=0)
    encoded = models.FileField(
        upload_to='files/artist/songs/encoded', blank=True, null=True)
    cover = models.ImageField(
        upload_to=redefinedFileName, null=True, blank=True)
    genres = models.ManyToManyField(Genre, blank=True)
    access_availability = models.ManyToManyField(
        AccessAvailability, blank=True)
    subscription: ArtistSubscription = models.ForeignKey(
        ArtistSubscription, null=True, blank=True, on_delete=models.CASCADE)
    duration_in_ms = models.IntegerField(default=0)
    isrc = models.CharField(max_length=17, null=True, blank=True)
    iswc = models.CharField(max_length=17, null=True, blank=True)
    publisher = models.CharField(max_length=35, null=True, blank=True)
    version = models.CharField(max_length=35, null=True, blank=True)
    writer = models.CharField(max_length=35, null=True, blank=True)
    composer = models.CharField(max_length=35, null=True, blank=True)
    arranger = models.CharField(max_length=35, null=True, blank=True)
    upc = models.CharField(max_length=17, null=True, blank=True)
    explicit = models.BooleanField(default=True)
    album_only = models.BooleanField(default=False)
    disseminated = models.BooleanField(default=False)
    lyrics = models.TextField(null=True, blank=True)
    label = models.ForeignKey(Label, null=True, on_delete=models.SET_NULL)
    eanupc = models.CharField(max_length=15, null=True, blank=True)
    preSalesDate = models.DateField(null=True)
    releaseEndDate = models.DateField(null=True)
    releaseStartDate = models.DateField(null=True)
    last_updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    directory_string_var = 'files/artist/songs/covers'
    song_dir = 'files/artist/songs'

    def __str__(self) -> str:
        return self.title

    @property
    def filesize(self):
        x = self.file.size
        return calculate_size(x)

    def save(self, **kwargs):
        self.cover = resizeImage(self.cover)
        super(Song, self).save(**kwargs)


class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    title = models.CharField(max_length=55)
    description = models.CharField(max_length=100)
    cover = models.ImageField(
        upload_to=redefinedFileName, null=True, blank=True)
    preSalesDate = models.DateField(null=True)
    originalReleaseDate = models.DateField(null=True)
    releaseEndDate = models.DateField(null=True)
    label = models.ForeignKey(Label, null=True, on_delete=models.SET_NULL)
    subscription = models.ForeignKey(
        ArtistSubscription, null=True, blank=True, on_delete=models.CASCADE)
    eanupc = models.CharField(max_length=15, null=True, blank=True)
    songs = models.ManyToManyField(Song, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    directory_string_var = 'files/artist/songs/covers'

    def __str__(self):
        return self.title


class AlbumMeta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    album = models.OneToOneField(Album, on_delete=models.CASCADE)
    distribute_id = models.CharField(max_length=11, null=True, blank=True)
    disseminated = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class RoyaltySplit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    royalty = models.ForeignKey(Royalty, null=True, on_delete=models.SET_NULL)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    fullname = models.CharField(max_length=105)
    share = models.FloatField()
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    total_paid = models.FloatField(null=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class SongSubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    song: Song = models.ForeignKey(Song, on_delete=models.CASCADE)
    subscription: ArtistSubscription = models.ForeignKey(
        ArtistSubscription, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class SongMeta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    song = models.OneToOneField(Song, on_delete=models.CASCADE)
    disseminate_id = models.CharField(max_length=10, null=True, blank=True)
    eveara_album = models.CharField(max_length=15, null=True, blank=True)
    djm_fingerprint_id = models.CharField(max_length=35, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class RadioPlay(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    radio_name = models.CharField(max_length=150)
    radio_id = models.CharField(max_length=150)
    query_date = models.DateField()
    duration = models.DurationField()
    timestamp = models.DateTimeField(auto_now_add=True)


class SongLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    storeName = models.CharField(max_length=150)
    link = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)


class SongDistributionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    step = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

