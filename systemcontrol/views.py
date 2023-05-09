from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework import filters

from django.http import Http404

from django_q.tasks import async_task

from .permissions import CanDisableArtist, CanViewArtist, CanDeleteArtist, IsFreeOrActiveMonitorSub
from .serializers import CountrySerializer, SystemDefaultSerializer, RadioFilterSerializer, FingerprintPlaySerializer
from .models import SystemDefault
from .cache import get_countries

from accounts.models import Artist
from accounts.permissions import IsArtist, IsStaff
from payouts.permissions import CanPayout
from accounts.serializers import GlobalArtistSerialzier, ArtistSerializer

from songs.models import Song
from songs.serializers import SongSerializer

from utils.api.djm import getStreamStatus, getRadioPlaylist, getFingerPlayed


class SystemDefaultListAPIView(generics.ListAPIView):
    queryset = SystemDefault.objects.all()
    serializer_class = SystemDefaultSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsStaff,
        permissions.DjangoModelPermissions
    )


class SystemDefaultDetailsAPIView(generics.RetrieveUpdateAPIView):
    queryset = SystemDefault.objects.all()
    serializer_class = SystemDefaultSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsStaff,
        permissions.DjangoModelPermissions
    )

    def perform_update(self, serializer):
        return serializer.save()


class RequestFingerPrint(generics.UpdateAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsArtist,
        IsFreeOrActiveMonitorSub
    )

    def perform_update(self, serializer):
        async_task('utils.api.djm.create_track_fingerprint',
                   track=self.get_object(), request=None)
        return serializer.save()


class RadioStreamAPIView(generics.GenericAPIView):
    serializer_class = RadioFilterSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        CanPayout
    )

    def get(self, request, **kwargs):
        status_code = status.HTTP_200_OK
        return Response(getStreamStatus(), status=status_code)

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        results = getRadioPlaylist(request.data)

        status_code = status.HTTP_200_OK
        return Response(results, status=status_code)


class FingerprintPlayedAPIView(generics.GenericAPIView):
    serializer_class = FingerprintPlaySerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        results = getFingerPlayed(request.data)

        status_code = status.HTTP_200_OK
        return Response(results, status=status_code)


class ArtistAdminAPIView(generics.ListAPIView):
    '''
        You can search for artist using the following: 
         Email, first name, last name, other names
         phone number, company name. \n
         You can filter by music class, state of residence, 
         local government area.
    '''
    queryset = Artist.objects.all().order_by('-date_joined')
    serializer_class = GlobalArtistSerialzier
    filter_backends = [filters.SearchFilter]
    permission_classes = (
        CanViewArtist,
    )
    search_fields = (
        'email',
        'first_name',
        'last_name',
        'other_names',
        'stage_name',
        'phone',
        'company_name',
        'music_class',
        'sor',
        'lga'
    )


class ArtistControlAPIView(generics.RetrieveDestroyAPIView):
    '''
        You can retrieve or delete Artist
    '''
    queryset = Artist.objects.all().order_by('-date_joined')
    serializer_class = ArtistSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        CanDeleteArtist
    )

    def get_object(self):

        try:
            artist = Artist.objects.select_related(
                'userphoto', 'artiststorage'
            ).get(pk=self.kwargs['artistId'])
            return artist
        except Artist.DoesNotExist:
            raise Http404

    def get_queryset(self):
        return self.get_object()

    def perform_destroy(self, instance):
        return instance.delete()

    def perform_update(self, serializer):
        return serializer.save()


class DisableArtistAPIView(generics.GenericAPIView):
    '''
      This API is used to deactivate artist.
      If artist account is been deactivated, they want be able to login.
    '''
    queryset = Artist.objects.all().order_by('-date_joined')
    serializer_class = ArtistSerializer
    permission_classes = (
        CanDisableArtist,
    )

    def get_object(self):

        try:
            artist = Artist.objects.select_related(
                'userphoto', 'artiststorage'
            ).get(pk=self.kwargs['artistId'])
            return artist
        except Artist.DoesNotExist:
            raise Http404

    def get(self, request, **kwargs):
        artist = self.get_object()
        artist.is_active = not artist.is_active
        artist.save()

        status_code = status.HTTP_200_OK
        return Response(ArtistSerializer(artist).data, status=status_code)


class CountryListAPIView(generics.ListAPIView):
    '''
        Get Country List
    '''
    serializer_class = CountrySerializer
    permission_classes = (
        permissions.AllowAny,
    )

    def get_queryset(self):
        return get_countries()
