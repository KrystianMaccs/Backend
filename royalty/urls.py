from django.urls import path

from .views import (
    ConfirmRoyalty,
    VerifyRoyalty,
    UpdateRoyaltyAPIView,
    AuthneticateRoyaltyAPIView,
)

urlpatterns = [
    path('confirm/', ConfirmRoyalty.as_view()),
    path('verify/', VerifyRoyalty.as_view()),
    path('authenticate/', AuthneticateRoyaltyAPIView.as_view()),
    path('account/update/<uuid:pk>/', UpdateRoyaltyAPIView.as_view()),
]
