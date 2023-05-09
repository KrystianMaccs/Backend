from django.urls import re_path, path

from .views import (
    ChargeListAPIView,
    ChargeDetailsAPIView,
    PayoutListAPIView,
    PayoutHistoryListAPIView,
    PayoutHistoryDetailAPIView,
    PayoutDetailAPIView,
    ArtistPayoutListAPIView,
    ArtistPayoutDetailsAPIView,
    SongSalesListAPIView,
    TriggerPayoutAPIView,

    SongSaleAPIView,
    RoyaltyPayoutListAPIView,
    RoyaltyPayoutRangeListAPIView,
    FailedArtistPayoutListAPIView,
    FailedRoyaltyPayoutListAPIView,
    ManualPaymentAPIView,
    ApprovePayoutAPIView,

    TrackTransferAPIView,
    ProcessingArtistPayoutListAPIView,
    ProcessingRoyaltyPayoutListAPIView,

    paystack_webhook,
)

urlpatterns = [
    path('charges/', ChargeListAPIView.as_view()),
    path('trigger/', TriggerPayoutAPIView.as_view()),
    path('royalty/', RoyaltyPayoutListAPIView.as_view()),
    path('start/payment/', ApprovePayoutAPIView.as_view()),
    path('manual/payment/', ManualPaymentAPIView.as_view()),
    path('charges/<uuid:pk>/', ChargeDetailsAPIView.as_view()),
    path('songsales/<uuid:song_id>/', SongSaleAPIView.as_view()),
    path('history/<uuid:payout>/', PayoutHistoryDetailAPIView.as_view()),

    path('paystack/listener/', paystack_webhook),

    re_path(r'^(?P<year>[0-9]{4})/$', PayoutListAPIView.as_view()),
    re_path(
        r'^annual/songsales/(?P<year>[0-9]{4})/$', SongSalesListAPIView.as_view()),
    re_path(r'^artist/(?P<year>[0-9]{4})/$',
            ArtistPayoutListAPIView.as_view()),
    re_path(r'^history/(?P<year>[0-9]{4})/$',
            PayoutHistoryListAPIView.as_view()),
    re_path(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
            PayoutDetailAPIView.as_view()),
    re_path(r'^artist/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
            ArtistPayoutDetailsAPIView.as_view()),
    re_path(r'^royalty/range/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
            RoyaltyPayoutRangeListAPIView.as_view()),
    re_path(r'^failed/artists/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
            FailedArtistPayoutListAPIView.as_view()),
    re_path(r'^failed/royalty/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
            FailedRoyaltyPayoutListAPIView.as_view()),
    re_path(r'^processing/artists/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
            ProcessingArtistPayoutListAPIView.as_view()),
    re_path(r'^processing/royalty/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
            ProcessingRoyaltyPayoutListAPIView.as_view()),

    re_path(r'^track-transfer/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
            TrackTransferAPIView.as_view()),
]
