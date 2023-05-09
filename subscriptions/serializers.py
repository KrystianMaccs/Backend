from django.contrib.sites.requests import RequestSite
from django.http.request import HttpRequest
from rest_framework import serializers
from django_q.tasks import async_task
from django.contrib.sites.shortcuts import get_current_site

from accounts.models import Artist
from songs.models import Album, Song, SongSubscription

from .models import Package, ArtistSubscription
from .utils import planIsValid, create_or_renew_plan

from utils.api.stripe import create_payment_intent


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        exclude = 'sku_id', 'eveara_id'


class ArtistSubscriptionSerializer(serializers.ModelSerializer):
    package_details = serializers.SerializerMethodField(read_only=True)
    reference = serializers.CharField(max_length=35)

    class Meta:
        model = ArtistSubscription
        fields = '__all__'
        read_only_fields = 'songs_added', 'expired', 'expired_timestamp'
        extra_kwargs = {
            'reference': {'write_only': True}
        }

    def to_representation(self, instance):
        subs = {
            "id": instance.id,
            "expired": instance.expired,
            "songs_added": instance.songs_added,
            "last_renewed": instance.last_renewed,
            "expired_timestamp": instance.expired_timestamp,
            "package": PackageSerializer(instance.package).data,
        }
        return subs

    def get_package_details(self, obj):
        return PackageSerializer(obj.package, read_only=True).data

    def create(self, validated_data):
        return create_or_renew_plan(validated_data)

    def update(self, instance, validated_data):
        return create_or_renew_plan(validated_data, instance=instance)


class SongPlanSerializer(serializers.Serializer):
    artist = serializers.ModelField(
        model_field=Artist._meta.get_field('id'))
    song = serializers.ModelField(model_field=Song._meta.get_field('id'))
    plan = serializers.ModelField(
        model_field=ArtistSubscription()._meta.get_field('id'))

    def create(self, validated_data):
        request = self.context['request']
        artist = request.user
        message = 'Number of songs exceed. You can not add song to the plan.'
        try:
            # artist = Artist.objects.get(pk=validated_data['artist'])
            plan: ArtistSubscription = ArtistSubscription.objects.select_related(
                "package").prefetch_related('song_set').get(pk=validated_data['plan'])
            if plan.artist != artist:
                raise serializers.ValidationError('Invalid Artist')

            song = Song.objects.get(pk=validated_data['song'])

            package: Package = plan.package

            # song_package_unique = ArtistSubscription.objects.filter()
            song_exists = SongSubscription.objects.filter(
                song_id=song.id, subscription__package__feature=package.feature).exists()

            if song_exists:
                raise serializers.ValidationError(
                    "Unable to add song to this subscription \
                        because this song is already added to a subscription of this type,\
                    you can only renew this song's subscription")

            if plan.songs_added < package.tracks_count:
                status, message = planIsValid(plan)
                if status:
                    song_init_sub = song.subscription
                    if song_init_sub != plan:
                        if song_init_sub is not None:
                            # Check old Subscription
                            song_init_sub.songs_added = song_init_sub.song_set.count() - 1
                            song_init_sub.save()

                        plan.songs_added = plan.song_set.count() + 1

                        SongSubscription.objects.get_or_create(
                            song=song,
                            subscription=plan
                        )

                        plan.save()
                        # song.subscription = plan
                        # song.save()

                        if plan.package.feature == Package.GO_DISTRO:
                            async_task('utils.api.eveara.upload_eveara_song',
                                       track=song, artist=artist, subscription=plan)

                        elif plan.package.feature == Package.GO_MONITOR:
                            # Fingerprint song
                            async_task('utils.api.djm.create_track_fingerprint',
                                       track=song, request=None)
                            ...
                    return plan

        except (Artist.DoesNotExist, ArtistSubscription.DoesNotExist, Song.DoesNotExist):
            raise serializers.ValidationError(
                "Invalid Field Enter Correct objects primary key")

        raise serializers.ValidationError(message)


class AlbumPlanSerializer(serializers.Serializer):
    artist = serializers.ModelField(
        model_field=Artist._meta.get_field('id'))
    album = serializers.ModelField(model_field=Album._meta.get_field('id'))
    plan = serializers.ModelField(
        model_field=ArtistSubscription()._meta.get_field('id'))

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        message = 'Number of songs exceed. You can not add song to the plan.'
        try:
            artist = Artist.objects.get(pk=validated_data['artist'])
            plan = ArtistSubscription.objects.select_related(
                'package').prefetch_related('song_set').get(pk=validated_data['plan'])
            if user != artist or plan.artist != artist:
                raise serializers.ValidationError('Invalid Artist')

            album = Album.objects.get(pk=validated_data['album'])

            package = plan.package
            album_song_count = album.songs.count()

            if album_song_count <= package.tracks_count:
                status, message = planIsValid(plan)
                if status:
                    album_init_sub = album.subscription
                    if album_init_sub != plan:
                        if album_init_sub is not None:
                            # Check old Subscription
                            album_init_sub = album_init_sub.songs_added - album_song_count
                            album_init_sub.save()

                        plan.songs_added = plan.songs_added + album_song_count
                        album.subscription = plan

                        plan.save()
                        album.save()

                    async_task('utils.api.eveara.album_upload',
                               album=album, subscription=plan)
                    return plan

        except (Artist.DoesNotExist, ArtistSubscription.DoesNotExist, Album.DoesNotExist):
            raise serializers.ValidationError(
                "Invalid Field Enter Correct objects primary key")

        raise serializers.ValidationError(message)


class StripePaySerializer(serializers.Serializer):
    package = serializers.ModelField(
        model_field=Package()._meta.get_field('id'))

    def create(self, validated_data):
        package_id = validated_data['package']

        package_filter = Package.objects.filter(id=package_id)
        if package_filter.exists():
            package: Package = package_filter.first()

            request: HttpRequest = self.context['request']
            user: Artist = request.user
            current_domain: RequestSite = get_current_site(request)

            secret: str = create_payment_intent(
                user, package)
            return secret

        raise serializers.ValidationError(
            "Subscription Package not found.")


class DistributeSerializer(serializers.Serializer):
    item = serializers.UUIDField()
    is_song = serializers.BooleanField()

    def create(self, validated_data):
        artist = self.context['request'].user
        is_song = validated_data.get('is_song', False)
        item = validated_data.get('item', None)

        message = 'Item is not valid'
        status = False

        if item is None:
            raise serializers.ValidationError(message)

        if is_song:
            item = Song.objects.select_related(
                'artist', 'artist__artistmeta', 'songmeta').prefetch_related(
                    'access_availability', 'genres').filter(id=item)

            if not item.exists():
                message = "Song is not valid"
                raise serializers.ValidationError(message)

        else:
            item = Album.objects.filter(id=item)

            if not item.exists():
                message = "Album is not valid"
                raise serializers.ValidationError(message)

        item = item.first()
        plan = item.subscription
        status, message = planIsValid(plan)

        if status:
            if is_song:
                d = ArtistSubscription.objects.filter(
                    songsubscription__song__id=item.id, package__feature=Package.GO_DISTRO)

                if d.exists():
                    plan = d.first()
                    async_task('utils.api.eveara.upload_eveara_song',
                            track=item, artist=artist, subscription=plan)
            else:
                async_task('utils.api.eveara.album_upload',
                           album=item, subscription=plan)

        if not status:
            raise serializers.ValidationError(message)

        return item
