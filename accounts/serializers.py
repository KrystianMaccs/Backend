from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

from django.utils import timezone

from .authentication import assign_token
from .models import Artist, ArtistStorage, BankAccount, UserPhoto, StaffProfile

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

User = get_user_model()


class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        exclude = 'user', 'change_password'


class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = '__all__'

    def get_permissions(self, obj):
        return obj.permissions.values('codename').all()


class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhoto
        fields = 'id', 'image'


class ArtistStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistStorage
        exclude = 'artist',


class UserSerializer(serializers.ModelSerializer):
    dp = serializers.SerializerMethodField(read_only=True)
    groups = GroupSerializer(read_only=True, many=True)
    profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        exclude = 'password', 'is_superuser', 'user_permissions'

    def get_dp(self, obj):
        try:
            return UserPhotoSerializer(obj.userphoto).data
        except:
            return None

    def get_profile(self, obj):
        try:
            return StaffProfileSerializer(obj.staffprofile).data
        except:
            return None


class ArtistSerializer(serializers.ModelSerializer):
    dp = serializers.SerializerMethodField(read_only=True)
    storage = serializers.SerializerMethodField(read_only=True)
    bvn_verified = serializers.SerializerMethodField(read_only=True)
    bank_account = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Artist
        exclude = 'password', 'verified',  'change_password',

    def get_dp(self, obj):
        return UserPhotoSerializer(obj.userphoto).data

    def get_storage(self, obj):
        return ArtistStorageSerializer(obj.artiststorage).data

    def get_bvn_verified(self, obj):
        return obj.verified

    def get_bank_account(self, obj):
        return BankAccountSerializer(obj.bankaccount).data


class GlobalArtistSerialzier(serializers.ModelSerializer):
    dp = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Artist
        exclude = ('password', 'verified',
                   'change_password', 'phone_verified')

    def get_dp(self, obj):
        return UserPhotoSerializer(obj.userphoto).data


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        exclude = 'artist', 'recipient_code'


class ArtistRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = (
            'email',
            'first_name',
            'last_name',
            'stage_name',
            'phone',
            'country_code',
            'country',
        )

    def create(self, validated_data):
        artist = Artist.objects.create_artist(**validated_data)
        return artist


class OTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)


class VerifyEmailSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    user = serializers.ReadOnlyField()
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user is not None :
            if user.is_active:
                jwt_token = assign_token(user)
                user.last_login = timezone.now()
                user.save()
                return {'user': user, 'token': jwt_token}
            raise serializers.ValidationError(
                "Account is not active please contact support")

        raise serializers.ValidationError("Email or password is incorrect")


class VerifyBVNSerializer(serializers.Serializer):
    # bvn = serializers.CharField(max_length=11)
    bank_name = serializers.CharField()
    account_number = serializers.CharField(max_length=11)
    bank_code = serializers.CharField(max_length=10)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class GlobalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = 'id', 'email', 'first_name', 'last_name'
        
class GlobalSSOArtistSerializer(serializers.ModelSerializer):
    dp = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Artist
        exclude = ('password', 'verified',
         'is_active',
          'date_joined',
          'last_login',
                   'change_password', 'phone_verified')

    def get_dp(self, obj):
        return UserPhotoSerializer(obj.userphoto).data
