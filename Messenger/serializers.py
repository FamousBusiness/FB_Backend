from rest_framework import serializers
from users.models import User
from .models import ChatModel


class MessengerUsersSerializer(serializers.ModelSerializer):

    class Meta:
        model  = User
        fields = ['id', 'name']

class ChatModelSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ChatModel
        fields = '__all__'
