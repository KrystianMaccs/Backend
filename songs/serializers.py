from typing import List
from rest_framework import serializers
from django.db.models import Prefetch
from django_q.tasks import async_task
from utils.api.eveara.outlets import get_song_link

from utils.api.eveara.songs import validate_album

from .models import (
    RadioPlay,
    Song,
    Album,
    Genre,
    Label,
    RoyaltySplit,
    AccessAvailability,
    SongDistributionLog,
    SongLink,
    SongSubscription,
)
from subscriptions.utils import planIsValid
from accounts.serializers import GlobalArtistSerialzier
from subscriptions.serializers import ArtistSubscriptionSerializer

from subscriptions.models import ArtistSubscription

from utils.song import (
    mb_2_byte,
    calculate_size,
    upload_calculator,
)
from .tasks import (
    check_split_limit,
    get_or_create_split,
    get_or_create_splitings
)

from utils.api.eveara import validate_song


def safe_dict_access(dict, key, default):
    try:
        return dict[key]
    except KeyError:
        return default


class ChangeSongsAlbumSerialzier(serializers.Serializer):
    old_album = serializers.UUIDField()
    new_album = serializers.UUIDField()
    songs = serializers.ListField(child=serializers.UUIDField())

    def get_song(self, pk):
        try:
            return Song.objects.get(pk=pk)
        except:
            raise serializers.ValidationError('Unknown Song '+pk)

    def validate(self, validated_data):
        old_album_pk = validated_data['old_album']
        new_album_pk = validated_data['new_album']
        song_pks = validated_data['songs']

        songs = [self.get_song(pk) for pk in song_pks]

        try:
            old_album = Album.objects.get(pk=old_album_pk)
            old_album_sub = old_album.subscription
            old_album.songs.remove(*songs)
            if old_album_sub is not None:
                old_album_sub.songs_added = old_album_sub.song_set.count() - len(songs)
                old_album_sub.save()
                async_task('utils.api.eveara.album_upload',
                           album=old_album, subscription=old_album.subscription)
        except:
            old_album = None

        try:
            new_album = Album.objects.get(pk=new_album_pk)

            new_song_count = len(songs)

            new_album_sub = new_album.subscription
            if new_album_sub is not None:
                package = new_album_sub.package
                album_song_count = new_album.songs.count()

                status = False
                message = 'Number of songs exceed. You can not add song to the plan.'

                if (album_song_count + new_song_count) <= package.tracks_count:
                    status, message = planIsValid(new_album_sub)
                    if status:
                        new_album.songs.add(*songs)
                        new_album_sub.songs_added = new_album_sub.song_set.count() + new_song_count
                        new_album_sub.save()
                        async_task('utils.api.eveara.album_upload',
                                   album=new_album, subscription=new_album_sub)

                if not status:
                    raise serializers.ValidationError(message)

            else:
                new_album.songs.add(*songs)

        except:
            new_album = None

        if new_album is None and old_album is None:
            raise serializers.ValidationError(
                'You need atleast one valid album to perform this perform.')

        return new_album if new_album is not None else old_album


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = 'title', 'id'


class AccessAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessAvailability
        fields = 'title', 'id'


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = 'id', 'title', 'description'


class RoyaltySplitSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoyaltySplit
        exclude = 'royalty',
        read_only_fields = 'paid', 'total_paid'

    def process_song_royalty(self, instance, data, instance_create=False):
        request = self.context['request']
        try:
            song = Song.objects.prefetch_related('royaltysplit_set').get(
                pk=data['song'].id if instance_create else instance.song_id)
            if request.user.id == song.artist_id:
                splitings = song.royaltysplit_set.all()
                split_valid, init_total = check_split_limit(
                    splitings)

                if split_valid:

                    total = 0

                    if instance_create:
                        total = init_total
                    else:
                        total = init_total - instance.share if init_total >= instance.share else init_total

                    total += data['share']

                    if total <= 100:
                        if instance_create:
                            instance = get_or_create_split(request, data, song)

                        if not instance_create:
                            instance.email = data['email']
                            instance.phone = data['phone']
                            instance.fullname = data['fullname']
                            instance.share = data['share']
                            instance.description = data.get('description', "")

                            royalty = instance.royalty

                            if royalty.username != data['email']:
                                splited = get_or_create_split(
                                    request, data, song, exist=True)
                                royalty = splited.royalty
                            else:
                                royalty.phone = data['phone']
                                royalty.save()

                            instance.royalty = royalty
                            instance.save()

                        return instance

            raise serializers.ValidationError(
                'Process terminated. Shares exceeded 100%')

        except Song.DoesNotExist:
            raise serializers.ValidationError(
                'Song not found !', code=404)

    def create(self, data):
        return self.process_song_royalty(
            instance=None,
            data=data,
            instance_create=True
        )

    def update(self, instance, data):
        return self.process_song_royalty(
            instance=instance,
            data=data,
            instance_create=False
        )


class SongSerializer(serializers.ModelSerializer):

    royalties = serializers.SerializerMethodField(read_only=True)
    file_size = serializers.SerializerMethodField(read_only=True)
    subscriptions = serializers.SerializerMethodField(read_only=True)

    genres = serializers.CharField()
    access_availability = serializers.CharField()

    genres_obj = serializers.SerializerMethodField(read_only=True)
    access_availability_obj = serializers.SerializerMethodField(read_only=True)
    # subscription = ArtistSubscriptionSerializer(read_only=True)
    label_obj = serializers.SerializerMethodField(read_only=True)

    fingerprint = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Song
        exclude = 'artist', 'subscription'
        read_only_fields = ('disseminated', 'subscription')
        extra_kwargs = {
            'genres': {'write_only': True},
            'access_availability': {'write_only': True}
        }

    def validate(self, attrs):
        file = attrs.get('file')
        intial_name: str = file.name
        file.name = intial_name.replace(' ', '-').lower()

        return super().validate(attrs)

    def get_subscriptions(self, obj):
        song_subs: List[SongSubscription] = obj.songsubscription_set.all()
        subs = (sub.subscription for sub in song_subs)
        return ArtistSubscriptionSerializer(subs, many=True).data

    def get_fingerprint(self, obj):
        return obj.songmeta.djm_fingerprint_id

    def get_file_size(self, obj):
        file_size = obj.file_size
        if file_size > 0:
            return calculate_size(file_size)
        obj.file_size = obj.file.size
        obj.save()
        return calculate_size(obj.file_size)

    def get_label_obj(self, obj):
        if obj.label:
            return LabelSerializer(obj.label).data
        return None

    def get_royalties(self, obj):
        return RoyaltySplitSerializer(obj.royaltysplit_set.all(), many=True).data

    def get_genres_obj(self, obj):
        return GenreSerializer(obj.genres, many=True).data

    def get_access_availability_obj(self, obj):
        return AccessAvailabilitySerializer(obj.access_availability, many=True).data

    def get_genre(self, title): return Genre.objects.get(title=title)

    def get_avail(self, title): return AccessAvailability.objects.get(
        title=title)

    def get_genres(self, genre_string):
        genres = genre_string.split(',')
        try:
            genres = [self.get_genre(title.strip())
                      for title in genres if title != '']
            return genres
        except Genre.DoesNotExist:
            raise serializers.ValidationError('Invalid Genre')

    def get_avails(self, avails_string):
        avails = avails_string.split(',')
        try:
            avails = [self.get_avail(title.strip())
                      for title in avails if title != '']
            return avails
        except AccessAvailability.DoesNotExist:
            raise serializers.ValidationError('Invalid Availability Access')

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        avails = validated_data.pop('access_availability')
        genres = validated_data.pop('genres')

        genres = self.get_genres(genres)
        avails = self.get_avails(avails)

        # success, message = validate_song(validated_data['file'])
        # if not success:
        #     raise serializers.ValidationError(message)
        # else:
        song = Song.objects.create(artist=user, **validated_data)
        song.genres.set([*genres])
        song.access_availability.set([*avails])

        song.save()
        return song

    def update(self, instance, validated_data):
        genres = validated_data.pop('genres')
        avails = validated_data.pop('access_availability')

        genres = self.get_genres(genres)
        avails = self.get_avails(avails)

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.isrc = safe_dict_access(validated_data, 'isrc', instance.isrc)
        instance.iswc = safe_dict_access(validated_data, 'iswc', instance.iswc)
        instance.explicit = safe_dict_access(
            validated_data, 'explicit', instance.explicit)
        instance.album_only = safe_dict_access(
            validated_data, 'album_only', instance.album_only)
        instance.preSalesDate = validated_data.get(
            'preSalesDate', instance.preSalesDate)
        instance.releaseEndDate = validated_data.get(
            'releaseEndDate', instance.releaseEndDate)
        instance.releaseStartDate = validated_data.get(
            'releaseStartDate', instance.releaseStartDate)

        instance.genres.set([*genres])
        instance.access_availability.set([*avails])

        instance.save()

        return instance


class ValidateSongSerializer(serializers.Serializer):
    audio = serializers.FileField()

    def create(self, validated_data):

        success, message = validate_song(validated_data['audio'])
        if success:
            return {
                "isValid": success,
                "message": message
            }
        else:
            raise serializers.ValidationError(message)


class AlbumSerializer(serializers.ModelSerializer):
    total_size = serializers.SerializerMethodField()
    total_songs_count = serializers.SerializerMethodField()
    subscription = ArtistSubscriptionSerializer(read_only=True)
    label = LabelSerializer()

    class Meta:
        model = Album
        exclude = 'artist', 'songs'
        read_only_fields = ('subscription',)

    def get_total_songs_count(self, obj):
        return obj.songs.count()

    def get_total_size(self, obj):
        songs = obj.songs.only('file').all()

        files = []

        for s in songs:
            try:
                files.append(upload_calculator(s.file.size))
            except Exception as e:
                print('File ', s.file, 'crashing')
                print(e)

        # files = [upload_calculator(s.file.size) for s in songs]
        total = mb_2_byte(sum(files))
        return calculate_size(total)

    def get_label(self, title):
        artist = self.context['request'].user
        self.artist = artist
        return Label.objects.get(title=title, artist=artist)

    def create(self, validated_data):
        label_data = validated_data.pop('label')

        album = Album.objects.create(**validated_data)

        try:
            label = self.get_label(label_data['title'])
            label.description = safe_dict_access(
                label_data, 'description', label.description)
            album.label = label
            album.save()
        except Label.DoesNotExist:
            label = Label.objects.create(
                title=label_data['title'], description=safe_dict_access(label_data, 'description', None), artist=self.artist)
            album.label = label

            album.save()

        return album

    def update(self, instance, validated_data):
        label_data = safe_dict_access(
            validated_data, 'label', instance.label)

        if not isinstance(label_data, Label) and label_data is not None:
            try:
                label = self.get_label(label_data['title'])
                label.description = safe_dict_access(
                    label_data, 'description', label.description)
                instance.label = label
            except Label.DoesNotExist:
                label = Label.objects.create(
                    title=label_data['title'], description=safe_dict_access(label_data, 'description', None), artist=self.artist)
                instance.label = label

        instance.title = safe_dict_access(
            validated_data, 'title', instance.title)
        instance.description = safe_dict_access(
            validated_data, 'description', instance.description)
        instance.cover = safe_dict_access(
            validated_data, 'cover', instance.cover)
        instance.originalReleaseDate = safe_dict_access(
            validated_data, 'originalReleaseDate', instance.originalReleaseDate)
        instance.eanupc = safe_dict_access(
            validated_data, 'eanupc', instance.eanupc)

        instance.save()

        return instance


class SongForm(serializers.Serializer):
    song = SongSerializer()
    royalties = RoyaltySplitSerializer(many=True)

    def validate(self, attrs):
        file = attrs.get('song').get('file')
        intial_name: str = file.name
        file.name = intial_name.replace(' ', '-').lower()
        return super().validate(attrs)


    def create(self, validated_data):
        song = validated_data['song']
        splits = validated_data['royalties']

        split_valid, total = check_split_limit(splits)
        if split_valid:
            obj_song = Song.objects.create(**song)
            # obj_song = Song(**song)
            request = self.context['request']
            obj_song.artist = request.user
            obj_song.save()
            async_task('royalty.serializers.get_or_create_splitings',
                       request, splits, obj_song)
            return obj_song

        raise serializers.ValidationError('Split is more than 100%')


class GlobalSongSerializer(serializers.ModelSerializer):
    subscription = ArtistSubscriptionSerializer(read_only=True)
    artist = GlobalArtistSerialzier(read_only=True)
    subscriptions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Song
        exclude = 'access_availability', 'genres'

    def get_subscriptions(self, obj):
        song_subs = obj.songsubscription_set.all()
        return ArtistSubscriptionSerializer(song_subs, many=True).data


class DistributeStatusSerializer(serializers.Serializer):
    target_id = serializers.UUIDField()
    is_album = serializers.BooleanField(default=False)
    is_fingerprint_req = serializers.BooleanField(default=False)

    def validate(self, attrs):
        super().validate(attrs)

        is_album = attrs.get('is_album')
        target = attrs.get('target_id')

        if is_album:
            obj = Album.objects.filter(id=target)
        else:
            obj = Song.objects.filter(id=target)

        if not obj.exists():
            raise serializers.ValidationError("Song or Album ID is required.")

        return attrs

    def create(self, validated_data):
        is_album = validated_data.get('is_album')
        target = validated_data.get('target_id')
        is_fingerprint_req = validated_data.get('is_fingerprint_req')

        def get_object(q): return q.first() if q.exists() else None

        if is_album:
            obj = Album.objects.filter(id=target)
        else:
            obj = Song.objects.filter(id=target)

        obj = get_object(obj)

        if obj is not None:
            if isinstance(obj, Song):
                if is_fingerprint_req:
                    async_task('utils.api.djm.create_track_fingerprint',
                               track=obj, request=None)
                    message = {
                        "status": True,
                        "message": "Your request is processing."
                    }
                    return message

                else:
                    meta = obj.songmeta
                    eveara_id = meta.eveara_album
            else:
                meta = obj.albummeta
                eveara_id = meta.distribute_id

            return validate_album(eveara_album_id=eveara_id)


class SongLinkSerializer(serializers.Serializer):
    target_id = serializers.UUIDField()
    is_album = serializers.BooleanField(default=False)

    def validate(self, attrs):
        super().validate(attrs)

        is_album = attrs.get('is_album')
        target = attrs.get('target_id')

        if is_album:
            obj = Album.objects.filter(id=target)
        else:
            obj = Song.objects.filter(id=target)

        if not obj.exists():
            raise serializers.ValidationError("Song or Album ID is required.")

        return attrs

    def create(self, validated_data):
        is_album = validated_data.get('is_album')
        target = validated_data.get('target_id')

        def get_object(q): return q.first() if q.exists() else None

        if is_album:
            obj = Album.objects.filter(id=target)
        else:
            obj = Song.objects.filter(id=target)

        obj = get_object(obj)

        if obj is not None:
            if isinstance(obj, Song):
                meta = obj.songmeta
                eveara_id = meta.eveara_album
            else:
                meta = obj.albummeta
                eveara_id = meta.distribute_id

            return get_song_link(eveara_album_id=eveara_id)


class RangeFingerprintPlaySerializer(serializers.Serializer):
    fingerprint_id = serializers.CharField()
    from_date = serializers.DateField()


class SavedSongLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongLink
        fields = 'storeName', 'link'


class RadioPlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = RadioPlay
        exclude = 'song',


class SongDistributionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongDistributionLog
        exclude = 'song',
