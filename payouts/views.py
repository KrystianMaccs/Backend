import hashlib

from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework import filters

from django.db.models import Prefetch
from django_q.tasks import async_task
from django.utils import timezone
from django.http import Http404

from datetime import datetime, timedelta, date
from utils.helper import get_next_month_ending

from payouts.tasks import transfer_listener

from .serializers import (
    ChargeSerializer,
    PayoutSerializer,
    SongSaleSerializer,
    ManualPaymentSeriaizer,
    ArtistPayoutSerializer,
    RoyaltyPayoutSerializer,
    PayoutHistorySerializer,
    TriggerPayoutSerializer,
    ArtistPayoutSerializerGB,
    ArtistIncludedPayoutSerializer,
)

from .models import (
    Charge,
    Payout,
    PayoutDue,
    SongSales,
    ArtistPayout,
    PayoutHistory,
    RoyaltyPayout
)

from .permissions import (
    CanPayout
)
from accounts.permissions import IsStaff
from royalty.permissions import IsRoyalty
from accounts.permissions import IsArtist, IsArtistOwner


class ChargeListAPIView(generics.ListCreateAPIView):
    '''
        This API is what admin use to create different charge 
        E.g Paystack, Gocreate, etc....
    '''
    queryset = Charge.objects.all()
    serializer_class = ChargeSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsStaff,
    )

    def perform_create(self, serializer):
        return serializer.save()


class ChargeDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Charge.objects.all()
    serializer_class = ChargeSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsStaff,
    )

    def perform_update(self, serializer):
        return serializer.save()

    def perform_destroy(self, instance):
        return instance.delete()


class PayoutListAPIView(generics.ListAPIView):
    serializer_class = PayoutSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsStaff,
    )

    def get_object(self):
        try:
            current_time = timezone.now()
            year = self.kwargs.get('year', current_time.year)
            payout = Payout.objects.select_related(
                'confirm_by', 'pay_due', 'payouthistory'
            ).filter(pay_due__due_date__year=year)
            return payout
        except:
            raise Http404

    def get_queryset(self):
        return self.get_object()


class PayoutHistoryListAPIView(generics.ListAPIView):
    serializer_class = PayoutHistorySerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsStaff,
    )

    def get_object(self):
        current_time = timezone.now()
        year = self.kwargs.get('year', current_time.year)
        history = PayoutHistory.objects.select_related('payout', 'payout__pay_due').filter(
            payout__pay_due__due_date__year=year
        ).order_by('payout__pay_due__due_date')
        return history

    def get_queryset(self):
        return self.get_object()


class PayoutHistoryDetailAPIView(generics.RetrieveAPIView):
    serializer_class = PayoutHistorySerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsStaff,
    )

    def get_object(self):
        try:
            history = PayoutHistory.objects.select_related('payout', 'payout__pay_due').get(
                payout__id=self.kwargs.get('payout'))
            return history
        except PayoutHistory.DoesNotExist:
            raise Http404

    def get_queryset(self):
        return self.get_object()


class PayoutDetailAPIView(generics.RetrieveAPIView):
    serializer_class = PayoutSerializer
    permission_classes = (
        CanPayout,
        permissions.IsAuthenticated,
    )

    def get_object(self):
        current_time = timezone.now()
        year = self.kwargs.get('year', current_time.year)
        month = self.kwargs.get('month', current_time.month-1)
        new_date = date(int(year), int(month), int(current_time.day))
        month_end = get_next_month_ending(new_date)
        try:
            payout = Payout.objects.select_related(
                'confirm_by', 'pay_due'
            ).get(pay_due__due_date__year=year, pay_due__due_date__month=month)

            return payout
        except Payout.DoesNotExist:
            pay_due, created = PayoutDue.objects.get_or_create(
                due_date=month_end)
            payout, created = Payout.objects.select_related(
                'pay_due').get_or_create(pay_due=pay_due)

            return payout

    def get_queryset(self):
        return self.get_object()


class ArtistPayoutListAPIView(generics.ListAPIView):
    serializer_class = ArtistPayoutSerializerGB
    permission_classes = (
        permissions.IsAuthenticated,
        IsArtist
    )

    def get_object(self):
        try:
            artist = self.request.user
            current_time = timezone.now()
            year = self.kwargs.get('year', current_time.year)
            payout = ArtistPayout.objects.select_related('approved_by', 'pay_due').filter(
                pay_due__due_date__year=year, artist=artist)
            return payout
        except:
            raise Http404

    def get_queryset(self):
        return self.get_object()


class ArtistPayoutDetailsAPIView(generics.RetrieveAPIView):
    serializer_class = ArtistPayoutSerializerGB
    permission_classes = (
        permissions.IsAuthenticated,
        IsArtist
    )

    def get_object(self):
        try:
            current_time = timezone.now()
            artist = self.request.user
            year = self.kwargs.get('year', current_time.year)
            month = self.kwargs.get('month', current_time.month-1)
            payout = ArtistPayout.objects.select_related('approved_by', 'pay_due').get(
                pay_due__due_date__year=year, pay_due__due_date__month=month, artist=artist)
            return payout
        except ArtistPayout.DoesNotExist:
            raise Http404

    def get_queryset(self):
        return self.get_object()


class SongSaleAPIView(generics.ListAPIView):
    '''
        Get all track sales details including the revenue, play count, etc
    '''
    serializer_class = SongSaleSerializer
    permission_class = (permissions.IsAuthenticated, IsArtist)

    def get_object(self):
        try:
            artist = self.request.user
            sales = SongSales.objects.select_related('pay_due', 'song').filter(
                song_id=self.kwargs.get('song_id'), song__artist=artist)
            return sales
        except:
            raise Http404

    def get_queryset(self):
        return self.get_object()


class SongSalesListAPIView(generics.ListAPIView):
    '''
        Get the song track details including the revenue, playcount, etc
    '''
    serializer_class = SongSaleSerializer
    permission_class = (permissions.IsAuthenticated, IsArtist)

    def get_object(self):
        try:
            artist = self.request.user
            current_time = timezone.now()
            year = self.kwargs.get('year', current_time.year)
            sales = SongSales.objects.select_related('pay_due', 'song').filter(
                pay_due__due_date__year=year, song__artist=artist).order_by('pay_due__due_date')
            return sales
        except:
            raise Http404

    def get_queryset(self):
        return self.get_object()


class RoyaltyPayoutListAPIView(generics.ListAPIView):
    serializer_class = RoyaltyPayoutSerializer
    permission_classes = (IsRoyalty,)

    def get_queryset(self):
        royalty = self.request.user
        return RoyaltyPayout.objects.prefetch_related(
            'royalty_split'
        ).filter(royalty=royalty).order_by('pay_due__due_date')


class RoyaltyPayoutRangeListAPIView(generics.ListAPIView):
    serializer_class = RoyaltyPayoutSerializer
    permission_classes = (IsRoyalty, )

    def get_object(self):
        royalty = self.request.user
        current_time = timezone.now()
        year = self.kwargs.get('year', current_time.year)
        month = self.kwargs.get('month', current_time.month-1)
        payouts = RoyaltyPayout.objects.prefetch_related(
            'royalty_split'
        ).filter(
            pay_due__due_date__year=year, pay_due__due_date__month=month, royalty=royalty).order_by('pay_due__due_date')
        return payouts

    def get_queryset(self):
        return self.get_object()


class FailedArtistPayoutListAPIView(generics.ListAPIView):
    '''
        This API route is used to get failed royalty payouts. 
        You can filter by year and month. If your want Failed Payout
        for the year along your pass 00 as the month value. 
        You can search by artist email, stage name, phone alone
    '''
    serializer_class = ArtistIncludedPayoutSerializer
    permission_classes = (permissions.IsAuthenticated,
                          permissions.DjangoObjectPermissions)
    filter_backends = [filters.SearchFilter]
    search_fields = ['artist__email', 'artist__stage_name', 'artist__phone']

    def get_queryset(self):
        current_time = timezone.now()
        year = self.kwargs.get('year', current_time.year)
        month = self.kwargs.get('month', 0)
        payouts = ArtistPayout.objects.select_related(
            'artist', 'approved_by', 'pay_due').filter(failed=True)
        payouts = payouts.filter(pay_due__due_date__year=year)

        if int(month) > 0:
            payouts = payouts.filter(pay_due__due_date__month=month)

        return payouts.order_by('pay_due__due_date')


class FailedRoyaltyPayoutListAPIView(generics.ListAPIView):
    '''
        This API route is used to get failed royalty payouts. 
        You can filter by year and month. If your want Failed Payout
        for the year along your pass 00 as the month value. 
    '''

    serializer_class = RoyaltyPayoutSerializer
    permission_classes = (permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions)

    def get_queryset(self):
        current_time = timezone.now()
        year = self.kwargs.get('year', current_time.year)
        month = self.kwargs.get('month', 0)
        payouts = RoyaltyPayout.objects.prefetch_related(
            'song_sale', 'royalty_split'
        ).filter(failed=True)

        payouts = payouts.filter(pay_due__due_date__year=year)

        if int(month) > 0:
            payouts = payouts.filter(pay_due__due_date__month=month)

        return payouts.order_by('pay_due__due_date')


class ProcessingArtistPayoutListAPIView(generics.ListAPIView):
    '''
        This API route is used to get processing royalty payouts. 
        You can filter by year and month. If your want Failed Payout
        for the year along your pass 00 as the month value. 
        You can search by artist email, stage name, phone alone
    '''
    serializer_class = ArtistIncludedPayoutSerializer
    permission_classes = (permissions.IsAuthenticated,
                          permissions.DjangoObjectPermissions)
    filter_backends = [filters.SearchFilter]
    search_fields = ['artist__email', 'artist__stage_name', 'artist__phone']

    def get_queryset(self):
        current_time = timezone.now()
        year = self.kwargs.get('year', current_time.year)
        month = self.kwargs.get('month', 0)
        payouts = ArtistPayout.objects.select_related(
            'artist', 'approved_by', 'pay_due').filter(is_processing=True)
        payouts = payouts.filter(pay_due__due_date__year=year)

        if int(month) > 0:
            payouts = payouts.filter(pay_due__due_date__month=month)

        return payouts.order_by('pay_due__due_date')


class ProcessingRoyaltyPayoutListAPIView(generics.ListAPIView):
    '''
        This API route is used to get processing royalty payouts. 
        You can filter by year and month. If your want Failed Payout
        for the year along your pass 00 as the month value. 
    '''

    serializer_class = RoyaltyPayoutSerializer
    permission_classes = (permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions)

    def get_queryset(self):
        current_time = timezone.now()
        year = self.kwargs.get('year', current_time.year)
        month = self.kwargs.get('month', 0)
        payouts = RoyaltyPayout.objects.prefetch_related(
            'song_sale', 'royalty_split'
        ).filter(is_processing=True)

        payouts = payouts.filter(pay_due__due_date__year=year)

        if int(month) > 0:
            payouts = payouts.filter(pay_due__due_date__month=month)

        return payouts.order_by('pay_due__due_date')


class TrackTransferAPIView(generics.GenericAPIView):
    '''
        Track transfer status.
    '''

    serializer_class = TriggerPayoutSerializer
    permission_classes = (permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions)

    def get(self, request, **kwargs):
        current_time = timezone.now()
        year = kwargs.get('year', current_time.year)
        month = kwargs.get('month', 0)
        pay_due = PayoutDue.objects.prefetch_related(
            Prefetch('artistpayout_set', ArtistPayout.objects.filter(
                is_processing=True, failed=False, paid=False)),
            Prefetch('royaltypayout_set', RoyaltyPayout.objects.filter(
                is_processing=True, failed=False, paid=False))
        ).get(due_date__year=year, due_date__month=month)

        # async_task('payouts.tasks.verify_transfers', pay_due)

        return Response({
            "status": True,
            "message": "Updating transfer records. Please check back later"
        }, status=status.HTTP_200_OK)


class ManualPaymentAPIView(generics.GenericAPIView):
    '''
     This Api is to confirm that the royalty or Artist has been paid outside the api.
    '''
    serializer_class = ManualPaymentSeriaizer
    permission_classes = (
        permissions.IsAuthenticated,
        CanPayout
    )

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_data = {
            "status": True,
            "message": "Paid",
        }

        status_code = status.HTTP_200_OK
        return Response(data=response_data, status=status_code)


class ApprovePayoutAPIView(generics.GenericAPIView):
    '''
        This API start approved the payment process.
    '''
    serializer_class = TriggerPayoutSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        CanPayout
    )

    def post(self, request, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payout = data.get('payout', None)
        try:
            payout = Payout.objects.get(id=payout)
            payout.confirm_by = request.user
            payout.approval_timestamp = timezone.now()
            payout.save()
            async_task('payouts.tasks.populate_artist_payout',
                       payout, request.user)
        except Payout.DoesNotExist:
            raise Http404

        response_data = {
            "status": True,
            "message": "Payout triggered",
        }

        status_code = status.HTTP_200_OK
        return Response(data=response_data, status=status_code)


class TriggerPayoutAPIView(generics.GenericAPIView):
    '''
        This API triggers the 3rd party API to revert the payment to gocreate.
        It doesnot start payment. The [ApprovePayout]  start the payment for artists and royalties
    '''
    serializer_class = TriggerPayoutSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        CanPayout
    )

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payout = serializer.save()
        response_data = {
            "status": True,
            "message": "Payout triggered",
            "payout": PayoutSerializer(payout).data
        }
        status_code = status.HTTP_200_OK
        async_task('payouts.tasks.update_song_payment_history', payout.pay_due)
        return Response(data=response_data, status=status_code)


@csrf_exempt
def paystack_webhook(request: HttpRequest):
    payload = request.body

    sig_header: str = request.META['x-paystack-signature']
    sha_signature = hashlib.sha256(sig_header.encode()).hexdigest()

    print(sig_header, sha_signature)

    if sha_signature == sig_header:
        event = payload.get('event')

        data = payload.get('data')

        if 'transfer.success' == event or 'transfer.failed':
            transfer_listener(data)

    return HttpResponse(status=200)
