from re import T
from rest_framework import serializers
from django.utils import timezone

from .models import (
    Charge,
    Payout,
    PayoutDue,
    SongSales,
    ArtistPayout,
    RoyaltyPayout,
    PayoutHistory,
)

from accounts.serializers import GlobalUserSerializer, GlobalArtistSerialzier
from songs.serializers import RoyaltySplitSerializer, GlobalSongSerializer


class ChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charge
        fields = '__all__'


class PayoutSerializer(serializers.ModelSerializer):
    confirm_by = GlobalUserSerializer(read_only=True)
    pay_due = serializers.StringRelatedField()

    class Meta:
        model = Payout
        fields = '__all__'


class SongSaleSerializer(serializers.ModelSerializer):
    # song = GlobalSongSerializer(read_only=True)
    pay_due = serializers.StringRelatedField()
    song_title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SongSales
        fields = '__all__'

    def get_song_title(self, obj):
        return obj.song.title


class GlobalSongSaleSerializer(serializers.ModelSerializer):
    song = GlobalSongSerializer(read_only=True)
    pay_due = serializers.StringRelatedField()

    class Meta:
        model = SongSales
        exclude = 'revenue', 'deduction',


class ArtistPayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistPayout
        exclude = 'artist',


class ArtistIncludedPayoutSerializer(serializers.ModelSerializer):
    artist = GlobalArtistSerialzier(read_only=True)
    approved_by = GlobalUserSerializer(read_only=True)
    pay_due = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ArtistPayout
        fields = '__all__'


class ArtistPayoutSerializerGB(serializers.ModelSerializer):
    pay_due = serializers.StringRelatedField(read_only=True)
    approved_by = GlobalUserSerializer(read_only=True)

    class Meta:
        model = ArtistPayout
        exclude = 'artist',


class GlobalArtistPayoutSerializer(serializers.ModelSerializer):
    artist = GlobalArtistSerialzier(read_only=True)

    class Meta:
        model = ArtistPayout
        fields = '__all__'


class PayoutHistorySerializer(serializers.ModelSerializer):
    pay_due = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PayoutHistory
        exclude = 'payout',

    def get_pay_due(self, obj):
        return str(obj.payout.pay_due)


class RoyaltyPayoutSerializer(serializers.ModelSerializer):
    royalty_split = RoyaltySplitSerializer(read_only=True, many=True)
    # song_sale = GlobalSongSaleSerializer(read_only=True, many=True)

    class Meta:
        model = RoyaltyPayout
        fields = '__all__'


class TriggerPayoutSerializer(serializers.Serializer):
    payout = serializers.UUIDField()

    def create(self, validated_data):
        payout = validated_data.get('payout')
        try:
            payout = Payout.objects.select_related('pay_due').get(id=payout)
            payout.song_tracked_count = 0
            payout.triggered = True
            payout.last_triggered = timezone.now()
            payout.save()
            return payout
        except Payout.DoesNotExist:
            raise serializers.ValidationError('Invalid Payout')


class ManualPaymentSeriaizer(serializers.Serializer):
    payout = serializers.UUIDField()
    # artist_payout_id = serializers.UUIDField(required=False)
    # royalty_payout_id = serializers.UUIDField(required=False)

    def create(self, validated_data):
        user = self.context['request'].user
        print(validated_data)
        payout = validated_data.get('payout')
        # royalty = validated_data.get('royalty_payout_id')
        # artist = validated_data.get('artist_payout_id')

        # print("Royalty "+str(royalty))
        # print("artist "+str(artist))
        try:
            artist_payout = ArtistPayout.objects.get(id=payout)
            artist_payout.approved_by = user
            artist_payout.failed = False
            artist_payout.paid = True
            artist_payout.save()
            return artist_payout
        except ArtistPayout.DoesNotExist:
            try:
                royalty_payout = RoyaltyPayout.objects.get(id=payout)
                royalty_payout.approved_by = user
                royalty_payout.failed = False
                royalty_payout.paid = True
                royalty_payout.save()
                return royalty_payout
            except RoyaltyPayout.DoesNotExist:
                raise serializers.ValidationError(
                    'Payout is not valid')
