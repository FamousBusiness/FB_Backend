from rest_framework import serializers



class RazorpaySerializer(serializers.Serializer):
    amount = serializers.CharField()



class MailPaymentSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    plan   = serializers.IntegerField()
   


class MailPaymentCompleteSerializer(serializers.Serializer):
    provider_order_id = serializers.CharField()
    payment_id        = serializers.CharField()
    signature_id      = serializers.CharField()

