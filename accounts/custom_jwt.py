from urllib import request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils.encoding import smart_str
from rest_framework import exceptions

from .models import Artist
from royalty.models import Royalty

from rest_framework.authentication import (
    get_authorization_header
)

# JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
# JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

# jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
# jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER

User = get_user_model()




class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        """
        Returns an active user that matches the payload's user id and email.
        """
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        username = user.username
        if not username:
            msg = _('Invalid token.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = Artist.objects.get_by_natural_key(username)

        except Artist.DoesNotExist:
            try:
                user = User.objects.get_by_natural_key(
                    username)

            except User.DoesNotExist:
                try:
                    user = Royalty.objects.get_by_natural_key(
                        username)

                except Royalty.DoesNotExist:
                    msg = _('Invalid signature.')
                    raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.AuthenticationFailed(msg)

        return self.get_user(validated_token), validated_token



# class GCJSONWebTokenAuthentication(BaseGCJSONWebTokenAuthentication):
#     """
#     Clients should authenticate by passing the token key in the "Authorization"
#     HTTP header, prepended with the string specified in the setting
#     `JWT_AUTH_HEADER_PREFIX`. For example:
#         Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
#     """
#     www_authenticate_realm = 'api'

#     def get_jwt_value(self, request):
#         auth = get_authorization_header(request).split()
#         auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

#         if not auth:
#             if api_settings.JWT_AUTH_COOKIE:
#                 return request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
#             return None

#         if smart_str(auth[0].lower()) != auth_header_prefix:
#             return None

#         if len(auth) == 1:
#             msg = _('Invalid Authorization header. No credentials provided.')
#             raise exceptions.AuthenticationFailed(msg)
#         elif len(auth) > 2:
#             msg = _('Invalid Authorization header. Credentials string '
#                     'should not contain spaces.')
#             raise exceptions.AuthenticationFailed(msg)

#         return auth[1]

#     def authenticate_header(self, request):
#         """
#         Return a string to be used as the value of the `WWW-Authenticate`
#         header in a `401 Unauthenticated` response, or `None` if the
#         authentication scheme should return `403 Permission Denied` responses.
#         """
#         return '{0} realm="{1}"'.format(api_settings.JWT_AUTH_HEADER_PREFIX, self.www_authenticate_realm)

# def assign_token(user):
#     payload = JWT_PAYLOAD_HANDLER(user)
#     jwt_token = JWT_ENCODE_HANDLER(payload)

#     return jwt_token
