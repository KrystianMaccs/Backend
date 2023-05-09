from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import GlobalSSOArtistSerializer
from sso.authentication import SSOAuthWebTokenAuthenticate

from .serializers import AppAccessAuthorizationSerializer, GetAccessTokenSerializer, SSOJWTAuthSerializer, SSOLoginSerializer


class SSOLoginAPIView(generics.GenericAPIView):
    '''
        This api route is used to login  
        artist via sso.
    '''

    serializer_class = SSOLoginSerializer
    permission_classes = (permissions.AllowAny, )

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        redirect_url = serializer.data['redirect_url']
        response = {
            'redirect_url': redirect_url,
        }

        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


class SSOJWTUserAPIView(generics.GenericAPIView):
    serializer_class = SSOJWTAuthSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        redirect_url = serializer.data['redirect_url']
        response = {
            'redirect_url': redirect_url,
        }

        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)




class SSOAuthorizationAPIView(generics.GenericAPIView):
    '''
        This api route is used to authenticate access token
    '''

    serializer_class = AppAccessAuthorizationSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = [SSOAuthWebTokenAuthenticate]

    def get(self, request, **kwargs):
        # serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        # serializer.is_valid(raise_exception=True)
        # artist = serializer.data['artist']

        artist = request.user
        response = {
            'artist': GlobalSSOArtistSerializer(artist).data,
        }

        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


class SSOAuthorizationAPIView(generics.GenericAPIView):
    '''
        This api route is used to authenticate access token
    '''

    serializer_class = AppAccessAuthorizationSerializer
    permission_classes = (permissions.IsAuthenticated, )
    # authentication_classes = [SSOAuthWebTokenAuthenticate]

    def get(self, request, **kwargs):
        # serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        # serializer.is_valid(raise_exception=True)
        # artist = serializer.data['artist']

        artist = request.user
        response = {
            'artist': GlobalSSOArtistSerializer(artist).data,
        }

        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


class SSOAuthorizationTokenRetrieveAPIView(generics.GenericAPIView):
    serializer_class = GetAccessTokenSerializer
    permission_classes = (permissions.AllowAny, )

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        jwt_token = serializer.save()['jwt_token']
        response = {
            'auth_token': jwt_token,
        }

        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


