import json
from typing import List
from django.db.models.query_utils import Q
from rest_framework import generics, status, permissions
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.http import Http404, response

from datetime import date, datetime

from accounts.models import Artist
from accounts.permissions import IsArtist
from songs.tasks import query_radioplay, update_songlink
from utils.api.djm.client import getFingerPlayed
from .permissions import (
    IsAritstVerified,
    IsSplitOwner,
    IsAlbumOwner,
    IsSongOwner,
    IsObjOwner
)

from .serializers import (
    RadioPlaySerializer,
    RangeFingerprintPlaySerializer,
    SavedSongLinkSerializer,
    SongDistributionLogSerializer,
    SongSerializer,
    AlbumSerializer,
    GenreSerializer,
    LabelSerializer,
    SongLinkSerializer,
    RoyaltySplitSerializer,
    ChangeSongsAlbumSerialzier,
    DistributeStatusSerializer,
    AccessAvailabilitySerializer,
    ValidateSongSerializer,
)
from .models import (
    Album,
    Song,
    Label,
    Genre,
    RoyaltySplit,
    AccessAvailability,
    SongDistributionLog,
    SongMeta,
    SongSubscription,
)
from utils.song import check_size


class GenreListAPIView(generics.ListAPIView):
    '''
        Song Genre List
    '''
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)


class AccessAvailabilityListAPIView(generics.ListAPIView):
    '''
        Access availbity for each song (Download, Stream...)
    '''
    queryset = AccessAvailability.objects.all()
    serializer_class = AccessAvailabilitySerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)


class LabelListAPIView(generics.ListCreateAPIView):
    '''
        Create a record label. This is important for distribution
    '''
    serializer_class = LabelSerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def get_queryset(self):
        return Label.objects.filter(artist=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(artist=self.request.user)


class LabelDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    '''
        Get Details, Update and Delete of Record Label
    '''
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    permission_classes = (permissions.IsAuthenticated, IsObjOwner)

    def perform_update(self, serializer):
        return serializer.save()

    def perform_destroy(self, instance):
        return instance.delete()


class RoyaltySplitCreateAPIView(generics.GenericAPIView):
    '''
        Create royalty spiltings.
    '''
    serializer_class = RoyaltySplitSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        split = serializer.save()

        status_code = status.HTTP_200_OK
        return Response(RoyaltySplitSerializer(split).data, status=status_code)


class ChangeSongsAlbumAPIView(generics.GenericAPIView):
    '''
        You can use this api to: \n
        1. Add Songs (multiple songs) to an album i.e
        the old_album field value will be null
        and the new_album field value will be the id of the album you want to add the songs to. \n

        2. Remove Songs (multiple songs) from an album i.e
        the old_album field value will be the id of the album you want to remove the song from and the new_album field value
        will be null.

        3. Move songs (multiple songs) to another album i.e
        the old_album field value will be the id of the album you want to remove the songs from
        and the new_album field value will be the id of the album you want to add the songs to
    '''
    serializer_class = ChangeSongsAlbumSerialzier
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        album = serializer.validated_data
        songs = Song.objects.prefetch_related(
            'royaltysplit_set', 'genres', 'access_availability',
            Prefetch('songsubscription_set',
                     SongSubscription.objects.select_related('subscription', 'subscription__package').all())).select_related(
            'label'
        ).filter(album=album)

        status_code = status.HTTP_200_OK
        return Response(SongSerializer(songs, many=True).data, status=status_code)


class ArtistAlbumAPIView(generics.ListCreateAPIView):
    '''
        Create Album or Get Album list API route.
    '''

    serializer_class = AlbumSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsAritstVerified)

    def get_queryset(self):
        return Album.objects.select_related('label').prefetch_related(
            Prefetch('songs', Song.objects.only('file').all())
        ).filter(artist=self.request.user).defer('songs')

    def perform_create(self, serializer):
        return serializer.save(
            artist=self.request.user
        )


class RoyaltySplitDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoyaltySplitSerializer
    queryset = RoyaltySplit.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsSplitOwner)

    def get_object(self):
        try:
            return RoyaltySplit.objects.select_related('song', 'song__artist').get(pk=self.kwargs['pk'])
        except:
            return Http404

    def perform_update(self, serializer):
        return serializer.save()

    def perform_destroy(self, instance):
        return instance.delete()


class SongListAPIView(generics.ListAPIView):
    '''
        Get songs using the album id.
    '''
    serializer_class = SongSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        album = self.kwargs.get('album')
        return Song.objects.prefetch_related(
            'royaltysplit_set', 'genres', 'access_availability',
            Prefetch('songsubscription_set',
                     SongSubscription.objects.select_related('subscription', 'subscription__package').all())).select_related(
            'label'
        ).filter(album__id=album)


class AllSongsListAPIView(generics.ListAPIView):
    serializer_class = SongSerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def get_queryset(self):
        return Song.objects.prefetch_related(
            'royaltysplit_set', 'genres', 'access_availability',
            Prefetch('songsubscription_set',
                     SongSubscription.objects.select_related('subscription', 'subscription__package').all())).select_related(
            'label'
        ).filter(artist=self.request.user)


class SongCreateAPIView(generics.GenericAPIView):
    '''
        Upload a new song using the album id as a parameter.
        The 404 error means the album ID is incorrect.

        Set the genres to like
        Fuji, Gospel, Etc..

        Do the same for the access_availability
    '''
    serializer_class = SongSerializer
    permission_classes = (permissions.IsAuthenticated, IsAritstVerified)

    def post(self, request, **kwargs):
        data = request.data
        user = request.user
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        status_code = status.HTTP_403_FORBIDDEN
        responseMessage = {
            'message': 'You need to verify your bvn before you can perform this action'
        }

        if isinstance(user, Artist):

            status_code = status.HTTP_400_BAD_REQUEST
            responseMessage['message'] = 'You dont have enough space.'

            file = data['file']
            storage = check_size(user.artiststorage, file.size)
            # storage = True
            if storage is not None:
                album = get_object_or_404(Album, pk=kwargs.get('album'))

                song = serializer.save()
                album.songs.add(song)
                storage.save()

                status_code = status.HTTP_200_OK
                song_id = song.id
                song = Song.objects.prefetch_related(
                    'royaltysplit_set', 'genres', 'access_availability',
                    Prefetch('songsubscription_set',
                             SongSubscription.objects.select_related('subscription', 'subscription__package').all())).select_related(
                    'label'
                ).get(
                    pk=song_id)

                responseMessage = SongSerializer(song).data
        return Response(responseMessage, status=status_code)


class AlbumDetailAPIView(generics.RetrieveUpdateAPIView):
    '''
        Update and retrieve an album details.
        It is adviceable to use PATCH method instead of PUT 
        if you want to change only the text and not the cover.
    '''

    serializer_class = AlbumSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsAlbumOwner,
    )

    def get_queryset(self):
        return Album.objects.filter(artist=self.request.user).defer('songs')

    def perform_update(self, serializer):
        return serializer.save(
            artist=self.request.user
        )


class SongDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    '''
        Retrieve, Delete or update a songs. 
    '''

    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsSongOwner
    )

    def get_object(self):
        try:
            return Song.objects.prefetch_related(
                'royaltysplit_set', 'genres', 'access_availability',
                Prefetch('songsubscription_set',
                         SongSubscription.objects.select_related('subscription', 'subscription__package').all())).select_related(
                'label'
            ).get(pk=self.kwargs['pk'])
        except:
            raise Http404

    def perform_update(self, serializer):
        return serializer.save(artist=self.request.user)

    def perform_destroy(self, instance):
        # instance.file.delete()
        return instance.delete()


class SubscriptionSongListAPIView(generics.GenericAPIView):
    '''
     Get all the songs under a subscription
    '''
    serializer_class = SongSerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def get(self, request, **kwargs):
        artist: Artist = request.user
        song_subs: List[SongSubscription] = SongSubscription.objects.prefetch_related(
            Prefetch('song', Song.objects.prefetch_related(
                'royaltysplit_set', 'genres', 'access_availability',
                Prefetch('songsubscription_set',
                         SongSubscription.objects.select_related('subscription', 'subscription__package').all())).select_related(
                'label'
            ))
        ).filter(song__artist_id=artist.id, subscription__id=kwargs.get('subscription'))

        songs = (sub.song for sub in song_subs)

        response = SongSerializer(songs, many=True).data
        return Response(status=200, data=response)


class SongDistributeStatusAPIView(generics.GenericAPIView):
    queryset = Song.objects.all()
    serializer_class = DistributeStatusSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        status_code = status.HTTP_200_OK
        data = serializer.save()
        return Response(data, status=status_code)


class SongLinkAPIView(generics.GenericAPIView):
    queryset = Song.objects.all()
    serializer_class = SongLinkSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        status_code = status.HTTP_200_OK
        data = serializer.save()
        return Response(data, status=status_code)


class RangeRadioMonitorAPIView(generics.GenericAPIView):
    serializer_class = RangeFingerprintPlaySerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def get(self, request, **kwargs):
        song_id = kwargs.get('song_id')
        month_count = kwargs.get('month_count')

        year: int = kwargs.get('year')
        month: int = kwargs.get('month')
        from_date = date(year=year,  month=month, day=1)

        song_query = Song.objects.select_related('songmeta').filter(pk=song_id)

        status_code = status.HTTP_400_BAD_REQUEST
        response_data = {
            'message': 'Song not found'
        }

        if song_query.exists():
            song: Song = song_query.first()

            radioplay_query = query_radioplay(song, from_date, month_count)

            response_data['message'] = 'Radio Monitoring Data'
            response_data['result'] = RadioPlaySerializer(
                radioplay_query, many=True).data
            status_code = status.HTTP_200_OK

        return Response(status=status_code, data=response_data)


class SavedSongLinkAPIView(generics.GenericAPIView):
    serializer_class = SavedSongLinkSerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def get_object(self):
        song_query = Song.objects.select_related('songmeta').filter(
            id=self.kwargs.get('song_id'), artist=self.request.user)

        song: Song = None
        if song_query.exists():
            song = song_query.first()

        return song

    def get(self, request, **kwargs):
        song = self.get_object()
        status_code = status.HTTP_400_BAD_REQUEST
        data = {'status': False, 'message': 'Song not found!'}

        if song is not None:
            status_code = status.HTTP_200_OK

            data['status'] = True
            data['message'] = 'Song links'
            data['results'] = SavedSongLinkSerializer(
                update_songlink(song), many=True).data

        return Response(status=status_code, data=data)


class ValidateSongAPIView(generics.GenericAPIView):
    serializer_class = ValidateSongSerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def post(self, request, **kwargs):

        data: dict = request.data

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        status_code = status.HTTP_200_OK
        payload = serializer.save()

        return Response(status=status_code, data=payload)


class SongDistributionLogListAPIView(generics.ListAPIView):
    serializer_class = SongDistributionLogSerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def get_queryset(self):
        artist = self.request.user
        return SongDistributionLog.objects.filter(
            song__artist=artist, song_id=self.kwargs.get('song_id')).order_by('-timestamp')
