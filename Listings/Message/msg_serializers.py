from rest_framework import serializers



class RazorpaySerializer(serializers.Serializer):
    amount = serializers.CharField()



class MessagePaymentSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    plan   = serializers.IntegerField()
   


class MessagePaymentCompleteSerializer(serializers.Serializer):
    provider_order_id = serializers.CharField()
    payment_id        = serializers.CharField()
    signature_id      = serializers.CharField()
    

        
class MessageSendSerializer(serializers.Serializer):
    category = serializers.IntegerField()
    message  = serializers.CharField()

