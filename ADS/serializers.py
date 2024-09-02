from rest_framework import serializers
from ADS.models import ADPLANS


class ADPaymentSerializer(serializers.Serializer):
    amount  = serializers.IntegerField()


class AdPaymentCompleteSerializer(serializers.Serializer):
    provider_order_id = serializers.CharField()
    payment_id        = serializers.CharField()
    signature_id      = serializers.CharField()



class AllADPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = ADPLANS
        fields = "__all__"

        
