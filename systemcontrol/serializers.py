from rest_framework import serializers

from .models import Country, SystemDefault


class SystemDefaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemDefault
        fields = '__all__'

        read_only_fields = ('nkey',)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = 'country_name', 'country_code'


class RadioFilterSerializer(serializers.Serializer):
    radio_stream_id = serializers.CharField()
    date = serializers.DateField()


class FingerprintPlaySerializer(serializers.Serializer):
    fingerprint_id = serializers.CharField()
    date = serializers.DateField()
