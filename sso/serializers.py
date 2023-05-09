from rest_framework import serializers
from django.contrib.auth import authenticate

from django.utils import timezone
from accounts.authentication import assign_token
from accounts.models import Artist
from sso.models import AppAuthLog, IdentityApp

from sso.tasks import get_access_token, get_client_ip, get_user_agent

ACCESS_TOKEN_EXP = 60

def validate_access_token(log: AppAuthLog) -> bool:
    now = timezone.now()

    gen_space = log.date_created - now

    return gen_space.seconds < ACCESS_TOKEN_EXP




class SSOLoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    public_key = serializers.CharField(write_only=True)
    redirect_url = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        request = self.context['request']
        user: Artist = authenticate(**data)
        public_key = data.get('public_key')

        app_query = IdentityApp.objects.only('id').filter(public_key=public_key)
        if app_query.exists():
            app: IdentityApp = app_query.first()

            if user is not None :
                if user.is_active:
                    token = get_access_token()

                    # token = assign_token(user)
                    access_token = f'{token}~{app.public_key}'

                    AppAuthLog.objects.create(
                        artist=user,
                        identity_app=app,
                        accessToken=access_token,
                        client_ip=get_client_ip(request),
                        client_user_agent=get_user_agent(request)
                    )
                    
                    redirect_url = f'{app.redirect_url}?access_token={access_token}'
                    return {'redirect_url': redirect_url}

                raise serializers.ValidationError(
                    "Account is not active please contact support")

            raise serializers.ValidationError("Email or password is incorrect")
        raise serializers.ValidationError("Identity application is unknown")

class SSOJWTAuthSerializer(serializers.Serializer):
    public_key = serializers.CharField(write_only=True)
    redirect_url = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        request = self.context['request']
        user: Artist = request.user
        public_key = data.get('public_key')

        app_query = IdentityApp.objects.only('id').filter(public_key=public_key)
        if app_query.exists():
            app: IdentityApp = app_query.first()

            if user is not None :
                if user.is_active:
                    token = get_access_token()

                    # token = assign_token(user)
                    access_token = f'{token}~{app.public_key}'

                    AppAuthLog.objects.create(
                        artist=user,
                        identity_app=app,
                        accessToken=access_token,
                        client_ip=get_client_ip(request),
                        client_user_agent=get_user_agent(request)
                    )
                    
                    redirect_url = f'{app.redirect_url}?access_token={access_token}'
                    return {'redirect_url': redirect_url}

                raise serializers.ValidationError(
                    "Account is not active please contact support")

            raise serializers.ValidationError("Authorization Error. Please login again.")
        raise serializers.ValidationError("Identity application is unknown")



class AppAccessAuthorizationSerializer(serializers.Serializer):
    private_key = serializers.CharField(write_only=True)
    access_token = serializers.CharField(write_only=True)
    artist = serializers.ReadOnlyField()

    def validate(self, data):
        super().validate(data)

        request = self.context['request']

        private_key = data.get('private_key')
        access_token = data.get('access_token')

        log_query = AppAuthLog.objects.select_related('artist').filter(
            identity_app__private_key=private_key,
            identity_app__is_active=True,
            accessToken=access_token
        )

        if log_query.exists():
            log: AppAuthLog   = log_query.first()

            auth_is_valid = validate_access_token(log)

            if auth_is_valid:

                log.approval_request_count += 1
                log.app_ip = get_client_ip(request)
                log.app_user_agent = get_user_agent(request)
                log.approval_request_timestamp = timezone.now()
                log.save()

                artist = log.artist

                return {'artist': artist}

            raise serializers.ValidationError("Authentication session expired")

        raise serializers.ValidationError("Authorization denied")


class GetAccessTokenSerializer(serializers.Serializer):
    secret = serializers.CharField()
    token = serializers.CharField()
    jwt_token = serializers.CharField(read_only=True)

    def create(self, validated_data):
        request = self.context['request']

        private_key = validated_data.get('secret')
        token = validated_data.get('token')

        log_query = AppAuthLog.objects.select_related('artist').filter(
            identity_app__private_key=str(private_key),
            identity_app__is_active=True,
            accessToken=str(token)
        )

        if log_query.exists():

            log: AppAuthLog = log_query.first()

            auth_is_valid = validate_access_token(log)

            if auth_is_valid:

                log.approval_request_count += 1
                log.app_ip = get_client_ip(request)
                log.app_user_agent = get_user_agent(request)
                log.approval_request_timestamp = timezone.now()
                log.save()

                artist = log.artist

                token = assign_token(artist)

                return {'jwt_token': token}

            raise serializers.ValidationError("Authentication session expired")

        raise serializers.ValidationError('Invalid access token or client secret')
