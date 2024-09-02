from rest_framework import serializers




class SoftwarePaymentCompleteSerializer(serializers.Serializer):
    provider_order_id = serializers.CharField()
    payment_id        = serializers.CharField()
    signature_id      = serializers.CharField()


class SoftwarePaymentSerializer(serializers.Serializer):
    amount  = serializers.IntegerField()