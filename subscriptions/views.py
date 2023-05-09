from django.http.request import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from accounts.permissions import IsArtist, IsStafpfOrReadOnly
from django.db.models import Prefetch
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from songs.models import Song
from songs.permissions import IsObjOwner

from .models import ArtistSubscription, Package
from utils.api.stripe import cancel_payment_intent, payment_webhook
from .serializers import (AlbumPlanSerializer, ArtistSubscriptionSerializer,
                          DistributeSerializer, PackageSerializer,
                          SongPlanSerializer, StripePaySerializer)


class PackageListAPIView(generics.ListCreateAPIView):
    '''
        Get packages that are available for subscription
    '''
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsStafpfOrReadOnly, )

    def perform_create(self, serializer):
        return serializer.save()


class PackageDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = (permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions, )

    def perform_update(self, serializer):
        return serializer.save()

    def perform_destroy(self, instance):
        return instance.delete()


class ArtistSubscriptionListAPIView(generics.ListCreateAPIView):
    '''
     Get an Artist subscriptions
    '''
    serializer_class = ArtistSubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def get_queryset(self):
        artist = self.request.user
        return ArtistSubscription.objects.select_related('package').prefetch_related(
            Prefetch('song_set', Song.objects.select_related('songmeta').all())).filter(
                artist=artist, provisioned=True)

    def perform_create(self, serializer):
        artist = self.request.user
        return serializer.save(artist=artist)


class ArtistSubscriptionDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = ArtistSubscription.objects.select_related(
        'package').prefetch_related('song_set').all()
    serializer_class = ArtistSubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated, IsObjOwner)

    def get_object(self):
        return ArtistSubscription.objects.select_related('package').prefetch_related(
            Prefetch('song_set', Song.objects.select_related('songmeta').all())).filter(
                artist=self.request.user, id=self.kwargs['pk'], provisioned=True)

    def perform_update(self, serializer):
        return serializer.save()


class SongPlanAPIView(generics.GenericAPIView):
    '''
        Add song to a subscription
    '''
    serializer_class = SongPlanSerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = serializer.save()

        status_code = status.HTTP_201_CREATED
        return Response(ArtistSubscriptionSerializer(instance=plan).data, status=status_code)


class AlbumPlanAPIView(generics.GenericAPIView):
    '''
        Add album to a subscription
    '''
    serializer_class = AlbumPlanSerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = serializer.save()

        status_code = status.HTTP_201_CREATED
        return Response(ArtistSubscriptionSerializer(instance=plan).data, status=status_code)


class RedistributionAPIView(generics.GenericAPIView):
    '''
        This api route allow artist to redistribute their songs. Incase of errors
    '''
    serializer_class = DistributeSerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        status_code = status.HTTP_200_OK
        response_data = {
            'status': True,
            'message': "You request is processing. Please check back later."
        }
        return Response(response_data, status=status_code)


class StripePaySubscription(generics.GenericAPIView):
    serializer_class = StripePaySerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_id: str = serializer.save()

        status_code = status.HTTP_200_OK
        response_data = {
            'status': True,
            'session_id': session_id,
            'message': "Payment Initialized",
        }
        return Response(response_data, status=status_code)


class StripeCancelPaymentAPIView(generics.GenericAPIView):
    serializer_class = StripePaySerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def get(self, request, **kwargs):
        client_secret: str = kwargs.get('client_secret')

        try:
            cancel_payment_intent(client_secret)
        except Exception as e:
            print('Payment Intent Cancel: ', e)

        status_code = status.HTTP_200_OK
        response_data = {
            'status': True,
            'message': "Payment Cancelled",
        }
        return Response(response_data, status=status_code)


@csrf_exempt
def stripe_webhook(request: HttpRequest):
    return payment_webhook(request)
