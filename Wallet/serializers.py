from rest_framework import serializers
from .models import Wallet, MatureWallet, ImmatureWallet



#### User Wallet Balance Serializer
class UserWalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = '__all__'



#### User Mature Wallet Balance Serializer
class UserMatureSerializer(serializers.ModelSerializer):

    class Meta:
        model  = MatureWallet
        fields = '__all__'



### User Immature Wallet Balance Serializer
class UserImmatureSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ImmatureWallet
        fields = '__all__'

