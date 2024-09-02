from .models import Banner
from rest_framework import serializers



class BannerPaymentSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    plan   = serializers.IntegerField()


class BannerPaymentCompleteSerializer(serializers.Serializer):
    provider_order_id = serializers.CharField()
    payment_id        = serializers.CharField()
    signature_id      = serializers.CharField()


class BannerUploadSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Banner
        fields = ['image', 'category', 'state', 'city']


class BannerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Banner
        fields = '__all__'
