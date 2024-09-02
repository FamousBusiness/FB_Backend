from rest_framework import serializers
from ADS.models import ADS



class RazorpaySerializer(serializers.Serializer):
    amount = serializers.CharField()



class ADPaymentSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    plan   = serializers.IntegerField()
   


class ADPaymentCompleteSerializer(serializers.Serializer):
    provider_order_id = serializers.CharField()
    payment_id        = serializers.CharField()
    signature_id      = serializers.CharField()
    

        
class ADPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = ADS
        fields = ['location', 'category', 'condition', 'title', 'description', 'price', 'tag', 'offer', 'img1', 'img2', 'img3', 'img4']


class AdSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ADS
        fields = '__all__'

    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        image_fields = ['img1', 'img2', 'img3', 'img4']

        for field in image_fields:
            if field in representation and representation[field]:
                image_path = f"https://api.famousbusiness.in/media/{representation[field]}"
                representation[field] = image_path

        return representation
