from django.urls import path

from .views import (
    SystemDefaultDetailsAPIView,
    SystemDefaultListAPIView,
    FingerprintPlayedAPIView,
    DisableArtistAPIView,
    ArtistControlAPIView,
    CountryListAPIView,
    ArtistAdminAPIView,
    RadioStreamAPIView,
    RequestFingerPrint,
)

urlpatterns = [
    path('', SystemDefaultListAPIView.as_view()),
    path('artists/', ArtistAdminAPIView.as_view()),
    path('countries/', CountryListAPIView.as_view()),
    path('radiostreams/', RadioStreamAPIView.as_view()),
    path('<uuid:pk>/', SystemDefaultDetailsAPIView.as_view()),
    path('fingerprint/played/', FingerprintPlayedAPIView.as_view()),
    path('requestfingerprint/<uuid:pk>/', RequestFingerPrint.as_view()),
    path('artist/disable/<uuid:artistId>/', DisableArtistAPIView.as_view()),
    path('artist/control/<uuid:artistId>/', ArtistControlAPIView.as_view()),
]
