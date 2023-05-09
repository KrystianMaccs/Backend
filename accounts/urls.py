from django.urls import path

from .views import (
    LoginAPIView,
    AuthUserAPIView,
    # ResendOTPAPIView,
    # VerifyOTPAPIView,
    VerifyEmailAPIView,
    UserPhotoUpdateView,
    ArtistDetailAPIView,
    ResetPasswordAPIView,
    ChangePasswordAPIView,
    BVNVerificationAPIView,
    ArtistRegistrationAPIView,
)

urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('user/', AuthUserAPIView.as_view()),
    path('verify/', VerifyEmailAPIView.as_view()),
    path('verify/bvn/', BVNVerificationAPIView.as_view()),
    path('register/', ArtistRegistrationAPIView.as_view()),
    path('artist/<uuid:pk>/', ArtistDetailAPIView.as_view()),
    path('change-password/', ChangePasswordAPIView.as_view()),
    path('user/dp/<uuid:pk>/', UserPhotoUpdateView.as_view()),
    # path('otp/resend/', ResendOTPAPIView.as_view()),
    # path('otp/verify/', VerifyOTPAPIView.as_view()),
    path('reset/password/', ResetPasswordAPIView.as_view()),
]
