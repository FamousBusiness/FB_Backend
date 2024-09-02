from rest_framework import serializers




class RazorpayorderSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    # currency = serializers.CharField()



class RazorPayOrderCompletionSerializer(serializers.Serializer):
    provider_order_id = serializers.CharField()
    payment_id        = serializers.CharField()
    signature_id      = serializers.CharField()
        