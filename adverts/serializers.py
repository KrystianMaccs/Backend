from django.db.models import fields
from rest_framework import serializers

from .models import Plan, Advert


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class AdvertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advert
        fields = '__all__'

    # def to_representation(self, instance):
    #     data = {
    #         "plan": None,
    #         "id": instance.id,
    #         "file": instance.file.url,
    #         "link": instance.link,
    #         "visits": instance.visits,
    #         "details": instance.details,
    #         "timestamp": instance.timestamp,
    #         "file_type": instance.file_type,
    #         "short_text": instance.short_text,
    #         "last_updated": instance.last_updated,
    #     }

    #     if instance.plan is not None:
    #         data['plan'] = PlanSerializer(instance.plan).data

    #     return data


class PublishAdvertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advert
        exclude = 'visits', 'plan'
