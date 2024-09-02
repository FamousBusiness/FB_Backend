from rest_framework import serializers
from Listings.models import TextMessage
from ADS.models import ADS
from Banner.models import Banner


class AdminADApproveSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ADS
        fields = ['verified']

class AdminMsgApproveSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TextMessage
        fields = ['verified']

class AdminBannerApproveSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Banner
        fields = ['verified']


class AdminMessageViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = TextMessage
        fields = "__all__"


class ListingsExcelUploadSerializer(serializers.Serializer):
        excel_file = serializers.FileField()



