from rest_framework import generics, permissions

from .models import Plan, Advert
from .serializers import (
    PlanSerializer, AdvertSerializer, PublishAdvertSerializer)

from accounts.permissions import IsStaff


class PlanListAPIView(generics.ListCreateAPIView):
    '''
        A plan is what the admin attach to an advert to delete when it expires
    '''
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = (permissions.IsAuthenticated, IsStaff)

    def perform_create(self, serializer):
        return serializer.save()


class PlanDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = (permissions.IsAuthenticated, IsStaff)

    def perform_update(self, serializer):
        return serializer.save()

    def perform_destroy(self, instance):
        return instance.delete()


class AllAdvertsAPIView(generics.ListCreateAPIView):
    queryset = Advert.objects.select_related('plan').all()
    serializer_class = AdvertSerializer
    permission_classes = (permissions.IsAuthenticated, IsStaff)

    def perform_create(self, serializer):
        return serializer.save()


class AdvertDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Advert.objects.select_related('plan').all()
    serializer_class = AdvertSerializer
    permission_classes = (permissions.IsAuthenticated, IsStaff)

    def perform_update(self, serializer):
        return serializer.save()

    def perform_destroy(self, instance):
        return instance.delete()


class PublicAdvertListAPIView(generics.ListAPIView):
    '''
        This is the api for publishing adverts.
    '''
    queryset = Advert.objects.select_related('plan').all().order_by('?')
    serializer_class = PublishAdvertSerializer
    permission_classes = (permissions.AllowAny, )
