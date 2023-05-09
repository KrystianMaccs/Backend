from rest_framework import serializers
from django.utils import timezone
from django_q.tasks import async_task

from .models import Royalty, RoyaltyProfile
from .tasks import verify_royalty_email

from accounts.tasks import verify_artist_email
from utils.api.paystack import validate_bvn


class RoyaltySerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = Royalty
        fields = 'fullname', 'email', 'phone',


class ConfirmRoyaltySerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        royalty, status, split_id = verify_royalty_email(
            data['uid'], data['token'])

        if status:
            return royalty, split_id

        raise serializers.ValidationError("Invalid Url")


class RoyaltyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoyaltyProfile
        exclude = 'royalty',

    def update(self, instance, validated_data):
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.other_names = validated_data['other_names']
        instance.bio = validated_data['bio']
        instance.save()

        return instance


class RoyaltySerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Royalty
        exclude = 'is_active',

    def get_profile(self, obj):
        try:
            return RoyaltyProfileSerializer(obj.royaltyprofile).data
        except:
            return None

    def update(self, instance, validated_data):
        profile = validated_data['profile']
        obj_profile = instance.profile

        first_name = profile['first_name']
        last_name = profile['last_name']
        other_names = profile['other_names']

        obj_profile.first_name = first_name
        obj_profile.last_name = last_name
        obj_profile.other_names = other_names

        instance.fullname = f'{first_name} {last_name} {other_names}'
        instance.phone = validated_data['phone']

        obj_profile.save()
        instance.save()

        return instance


class RoyaltyBankSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=19)
    bvn = serializers.CharField(max_length=19)
    bank_name = serializers.CharField()
    bank_code = serializers.CharField()

    def validate(self, data):
        royalty = self.context['request'].user
        if isinstance(royalty, Royalty):
            profile = royalty.royaltyprofile

            bvn = data['bvn']
            account_number = data['account_number']
            bank_code = data['bank_code']

            # status, msg = validate_bvn(profile.first_name, profile.last_name, bvn,
            #                            account_number, profile.other_names, bank_code)

            status, msg = True, None

            if not status:
                raise serializers.ValidationError(msg)

            profile.bank_code = bank_code
            profile.account_number = account_number
            profile.bank_name = data['bank_name']
            profile.is_verified = status
            profile.last_updated = timezone.now()
            profile.save()

            async_task('utils.api.paystack.create_recipient',
                       royalty_profile=profile)

            return royalty

        raise serializers.ValidationError("This account is not valid")
