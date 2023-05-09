from django.urls import path
from .views import (PackageDetailAPIView,
                    PackageListAPIView,
                    AlbumPlanAPIView,
                    RedistributionAPIView,

                    ArtistSubscriptionListAPIView,
                    ArtistSubscriptionDetailAPIView,
                    SongPlanAPIView,
                    StripePaySubscription,
                    StripeCancelPaymentAPIView,
                    stripe_webhook)


urlpatterns = [
    path('stripewebhook/', stripe_webhook),
    path('song/add/', SongPlanAPIView.as_view()),
    path('album/add/', AlbumPlanAPIView.as_view()),
    path('package/', PackageListAPIView.as_view()),
    path('redistribute/', RedistributionAPIView.as_view()),
    path('stripepayment/', StripePaySubscription.as_view()),
    path('artist/', ArtistSubscriptionListAPIView.as_view()),
    path('package/<uuid:pk>/', PackageDetailAPIView.as_view()),
    path('artist/<uuid:pk>/', ArtistSubscriptionDetailAPIView.as_view()),
    path('stripepayment/cancel/<str:client_secret>/',
         StripeCancelPaymentAPIView.as_view()),
]
