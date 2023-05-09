from django.urls import path

from sso.views import (SSOAuthorizationAPIView,
 SSOLoginAPIView, SSOJWTUserAPIView,
 SSOAuthorizationTokenRetrieveAPIView)

urlpatterns = [
    path('authenticate/', SSOLoginAPIView.as_view()),
    path('request/auth/', SSOJWTUserAPIView.as_view()),
    path('authorize/', SSOAuthorizationAPIView.as_view()),
    path('request/auth/token/', SSOAuthorizationTokenRetrieveAPIView.as_view()),
]

