from rest_framework import generics, status, permissions
from rest_framework.response import Response

from django.utils import timezone

from .models import Royalty, RoyaltyProfile
from .permissions import IsRoyalty, IsProfileOwner
from .serializers import (RoyaltySerializer, RoyaltyProfileSerializer,
                          RoyaltyBankSerializer, ConfirmRoyaltySerializer)
# from accounts.authentication import assign_token
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from utils.api.twilio import verify_otp

from songs.models import RoyaltySplit


class ConfirmRoyalty(generics.GenericAPIView):
    '''
        Just like the verify email api, this API works similarly
    '''
    serializer_class = ConfirmRoyaltySerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        royalty, split_id = serializer.validated_data

        status_code = status.HTTP_200_OK
        return Response(RoyaltySerializer(royalty).data, status=status_code)


class AuthneticateRoyaltyAPIView(generics.GenericAPIView):
    '''
        This API is used to authenticate royalty alone.
        If the authentication is sucessfull they will be 
        granted an authorization token.
    '''
    serializer_class = ConfirmRoyaltySerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        data = request.data
        otp = data['otp']

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        royalty, split_id = serializer.validated_data

        valid, message = verify_otp(royalty.phone, otp)

        if valid:
            profile = RoyaltyProfile.objects.get_or_create(royalty=royalty)

        response = {
            'status': valid,
            'message': 'OTP Verified'
        }

        status_code = status.HTTP_200_OK

        if not valid:
            response['message'] = message
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            royalty.is_active = True
            royalty.last_authenticated = timezone.now()
            royalty.save()

            response = {
                'status': valid,
                'access_token': AccessToken.for_user(royalty),
                'refresh_token': RefreshToken.for_user(royalty),
                'royalty': RoyaltySerializer(royalty).data
            }

        try:
            split = RoyaltySplit.objects.get(pk=split_id)
            split.is_verified = True
            split.save()
        except:
            response['message'] = 'Song not found'
            status_code = status.HTTP_400_BAD_REQUEST

        return Response(response, status=status_code)


class UpdateRoyaltyAPIView(generics.UpdateAPIView):
    '''
        This Updates the Royalty Profile.
    '''
    permission_classes = (IsProfileOwner, )
    serializer_class = RoyaltyProfileSerializer
    queryset = RoyaltyProfile.objects.all()

    def perform_update(self, serializer):
        return serializer.save()


class VerifyRoyalty(generics.GenericAPIView):
    '''
        Verify the royalty bank account information with this API.
    '''
    serializer_class = RoyaltyBankSerializer
    permission_classes = (IsRoyalty, )

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        royalty = serializer.validated_data

        status_code = status.HTTP_200_OK
        return Response(RoyaltySerializer(royalty).data, status=status_code)
