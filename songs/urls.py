from django.urls import path

from .views import (
    ArtistAlbumAPIView,
    SavedSongLinkAPIView,
    SongDistributionLogListAPIView,
    SongListAPIView,
    SubscriptionSongListAPIView,
    AlbumDetailAPIView,
    SongDetailAPIView,
    SongCreateAPIView,
    RoyaltySplitCreateAPIView,
    RoyaltySplitDetailAPIView,
    GenreListAPIView,
    LabelListAPIView,
    LabelDetailAPIView,
    AccessAvailabilityListAPIView,

    SongLinkAPIView,
    AllSongsListAPIView,
    ChangeSongsAlbumAPIView,
    SongDistributeStatusAPIView,

    RangeRadioMonitorAPIView,
    ValidateSongAPIView
)


urlpatterns = [
    path('links/', SongLinkAPIView.as_view()),
    path('all/', AllSongsListAPIView.as_view()),
    path('labels/', LabelListAPIView.as_view()),
    path('genres/', GenreListAPIView.as_view()),
    path('albums/', ArtistAlbumAPIView.as_view()),
    path('<uuid:album>/', SongListAPIView.as_view()),
    path('labels/<uuid:pk>/', LabelDetailAPIView.as_view()),
    path('new/<uuid:album>/', SongCreateAPIView.as_view()),
    path('albums/<uuid:pk>/', AlbumDetailAPIView.as_view()),
    path('details/<uuid:pk>/', SongDetailAPIView.as_view()),
    path('album/change/', ChangeSongsAlbumAPIView.as_view()),
    path('royalty/add/', RoyaltySplitCreateAPIView.as_view()),
    path('access/available/', AccessAvailabilityListAPIView.as_view()),
    path('distribution/status/', SongDistributeStatusAPIView.as_view()),
    path('royalty/details/<uuid:pk>/', RoyaltySplitDetailAPIView.as_view()),

    path('distro/logs/<uuid:song_id>/', SongDistributionLogListAPIView.as_view()),

    path('saved/links/<uuid:song_id>/', SavedSongLinkAPIView.as_view()),
    path('validate/', ValidateSongAPIView.as_view()),

    path('subscriptions/<uuid:subscription>/',
         SubscriptionSongListAPIView.as_view()),

    path('radio-monitor/collection/<uuid:song_id>/<int:year>/<int:month>/<int:month_count>/',
         RangeRadioMonitorAPIView.as_view()),
]
