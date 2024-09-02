from rest_framework import serializers
from Listings.models import Order, ClientOrder, Wallet


#For All Business Owner+
class BusinessTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'


#For those who donot have a business page
class ClientTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientOrder
        fields = '__all__'


class WalletSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Wallet
        fields = '__all__'