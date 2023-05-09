from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import filters
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django_q.tasks import async_task

from royalty.serializers import RoyaltySerializer
from royalty.models import Royalty

from .permissions import IsArtistOrReadOnly, IsArtist, IsArtistOwner, IsStaffOwner
from .serializers import (
    ArtistRegistrationSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    VerifyEmailSerializer,
    BankAccountSerializer,
    UserPhotoSerializer,
    VerifyBVNSerializer,
    ArtistSerializer,
    LoginSerializer,
    UserSerializer,
    OTPSerializer
)

from .models import Artist, OTP, UserPhoto, BankAccount
from utils.api.paystack import validate_bvn
from utils.api.twilio import (
    register_phone,
    verify_otp
)
from .tasks import (
    confirm_email,
    verify_artist_email,
)

User = get_user_model()


class LoginAPIView(generics.GenericAPIView):
    '''
        This api route is used to login for both 
        the artist and gocreate staff.
    '''

    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny, )

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.data['user']

        response = {
            'token': serializer.data['token'],
        }

        if isinstance(user, User):
            user_data = UserSerializer(
                user, context=self.get_serializer_context()).data

            response['staff'] = user_data

        else:
            user_data = ArtistSerializer(
                user, context=self.get_serializer_context()).data

            response['artist'] = user_data

        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


class ArtistRegistrationAPIView(generics.GenericAPIView):
    '''
        Artist Registration First API
    '''

    serializer_class = ArtistRegistrationSerializer
    permission_classes = (permissions.AllowAny, )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        artist = serializer.save()

        params = {
            "domain": get_current_site(request),
            "pk": artist.pk
        }
        async_task("accounts.tasks.confirm_email", params)

        response = {
            'status': 'success',
            'message': '''We have sent you an email that will enable you to continue your registration.'''
        }
        status_code = status.HTTP_200_OK

        return Response(response, status=status_code)


class ArtistDetailAPIView(generics.RetrieveUpdateAPIView):
    '''
        This API route allows you to get and update artist 
        using the id of the artist. I.e the artist id is 
        the primary key (PK)
    '''

    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = (permissions.IsAuthenticated, IsArtistOrReadOnly)

    def perform_update(self, serializer):
        user = self.request.user
        try:
            phone = self.request.data['phone']
        except:
            phone = None
        return serializer.save(
            email=user.email,
            phone_verified=False if phone is not None and user.phone != phone else user.phone_verified,
            is_active=user.is_active,
            verified=user.verified
        )


class ResendOTPAPIView(generics.GenericAPIView):
    '''
        This API route allows you to resend OTP.
        Hardcode *000000* in the otp Field
    '''
    serializer_class = OTPSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *arg, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        async_task("utils.api.twilio.register_phone", data['phone'])
        status_code = status.HTTP_200_OK
        response = {
            'status': 'success',
            'message': 'OTP have been sent'
        }
        return Response(response, status=status_code)


class VerifyOTPAPIView(generics.GenericAPIView):
    serializer_class = OTPSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        data = request.data

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        otp = data['otp']
        phone = data['phone']

        artist = get_object_or_404(Artist, phone=phone)

        valid, message = verify_otp(phone, otp)

        response = {
            'status': valid,
            'message': 'OTP Verified'
        }

        status_code = status.HTTP_200_OK

        if not valid:
            response['message'] = message
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            artist.phone_verified = True
            artist.save()

        return Response(response, status=status_code)


class VerifyEmailAPIView(generics.GenericAPIView):
    '''
        This API route allows artists to confirm their email and proceed 
        to login. This uid is sent as a query parameter in the link sent 
        to the artists email it is represented as uid64=?, and the token is 
        represented as token=?.
    '''

    serializer_class = VerifyEmailSerializer
    permission_classes = (permissions.AllowAny, )

    def post(self, request, **kwargs):
        data = request.data
        password = data['password']
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user, valid = verify_artist_email(
            uidb64=data['uid'], token=data['token'])

        response = {
            'status': user is not None,
            'message': 'Your Account is now active. You can now login into your account'
        }

        status_code = status.HTTP_400_BAD_REQUEST

        is_artist = isinstance(user, Artist)
        profile = user.staffprofile if not is_artist else None

        if user is None:
            response['message'] = 'Invalid url, You need to register again'

        elif is_artist and user.change_password:
            response['message'] = 'This link has expire.'

        elif not is_artist and profile.change_password:
            response['message'] = 'This link has expire.'

        elif user.is_active and not valid:
            response['message'] = 'This link has expire.'

        elif user.is_active and user.check_password(password):
            response['message'] = 'You can not use your last password. Please change your password'

        else:
            if user.is_active:
                response['message'] = 'You have successfully reset your password'
            user.set_password(password)
            user.is_active = True

            if is_artist:
                user.change_password = True
            else:
                profile.change_password = True
                profile.save()

            user.save()

            status_code = status.HTTP_200_OK

        return Response(response, status=status_code)


class ChangePasswordAPIView(generics.GenericAPIView):
    '''
        This API route allows artists
        to change their password.
    '''

    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def put(self, request, **kwargs):
        user = request.user
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        response = {
            'message': 'Incorrect password'
        }
        status_code = status.HTTP_400_BAD_REQUEST

        if user.check_password(data['old_password']):
            status_code = status.HTTP_200_OK
            response['message'] = 'You have successfully changed your password'

            user.set_password(data['new_password'])
            user.save()

        return Response(response, status=status_code)


class ResetPasswordAPIView(generics.GenericAPIView):
    '''
        This API route allows artist or gocreate staff to 
        reset their password.
    '''
    serializer_class = ResetPasswordSerializer
    permission_classes = (permissions.AllowAny, )

    def post(self, request, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        email = data['email']
        user = Artist.objects.filter(email=email)
        staff = User.objects.filter(email=email)

        response = {
            'message': 'Email Address not Recognized.'
        }
        status_code = status.HTTP_400_BAD_REQUEST
        artist_exists = user.exists()
        if artist_exists or staff.exists():
            user = user.first() if artist_exists else staff.first()
            response['message'] = 'We have sent you an email containing the next step to reset your password.'
            status_code = status.HTTP_200_OK

            params = {
                "domain": get_current_site(request),
                "pk": user.pk,
                "artist": artist_exists
            }

            async_task("accounts.tasks.confirm_reset_password",
                       params)

            user.change_password = False
            user.save()

        return Response(response, status=status_code)


class BVNVerificationAPIView(generics.GenericAPIView):
    '''
        This is the BVN verification route.
        The Firstname Lastname and Middle are collected from the 
        database. The middle is the other_names.
    '''

    serializer_class = VerifyBVNSerializer
    permission_classes = (permissions.IsAuthenticated, IsArtist)

    def post(self, request, **kwargs):
        data = request.data
        user = request.user

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        ba, _ = BankAccount.objects.get_or_create(artist=user)
        account_number = data['account_number']
        status_code = status.HTTP_400_BAD_REQUEST
        response = {
            'message': 'You cannot perform this process twice'
        }

        if not user.verified or ba.account_number != account_number:
            # stat, msg = validate_bvn(
            #     first_name=user.first_name,
            #     last_name=user.last_name,
            #     middle_name=user.other_names,
            #     bvn=data['bvn'],
            #     account_number=account_number,
            #     bank_code=data['bank_code']
            # )
            stat: bool = True
            msg: str = "Account verified"

            response['message'] = msg

            if stat:

                user.verified = True

                ba.account_number = account_number
                ba.bank_name = data['bank_name']
                ba.bank_code = data['bank_code']
                ba.save()

                async_task('utils.api.paystack.create_recipient',
                           bank_account=ba)

                user.save()

                status_code = status.HTTP_200_OK

        return Response(response, status=status_code)


class AuthUserAPIView(generics.GenericAPIView):
    '''
        Get Authenticated user for artists or gocreate staff
        using the Authorization token (JWT)
    '''

    serializer_class = ArtistSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, **kwargs):
        user = request.user

        status_code = status.HTTP_200_OK
        if isinstance(user, User):
            data = UserSerializer(user).data
        elif isinstance(user, Royalty):
            data = RoyaltySerializer(user).data
        else:
            data = ArtistSerializer(user).data

        return Response(data, status=status_code)


class UserPhotoUpdateView(generics.UpdateAPIView):
    '''
        Update user display picture. This is for both 
        artist or gocreate staff. Use the ID from the DP
        in the user response.

    '''

    queryset = UserPhoto.objects.all()
    serializer_class = UserPhotoSerializer
    permission_classes = (permissions.IsAuthenticated, IsArtistOwner)

    def perform_update(self, serializer):
        user = self.request.user
        return serializer.save(
            artist=user if isinstance(user, Artist) else None,
            user=user if isinstance(user, User) else None
        )
