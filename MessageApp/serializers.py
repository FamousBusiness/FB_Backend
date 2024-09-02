from rest_framework import serializers
from Lead.models import BusinessPageLeadBucket, Lead



class SMSSerializer(serializers.Serializer):
    sms = serializers.CharField()


class LeadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Lead
        fields ='__all__'



class PaidLeadSerializers(serializers.ModelSerializer):
    lead = LeadSerializer()

    class Meta:
        model = BusinessPageLeadBucket
        fields = ('lead',) 