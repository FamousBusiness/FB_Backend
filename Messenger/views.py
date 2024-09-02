from django.shortcuts import render
from users.models import User
from django.http import HttpResponse
from Messenger.models import ChatModel
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from .serializers import MessengerUsersSerializer, ChatModelSerializer
from rest_framework import status



class MessngerUsersListApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = User.objects.exclude(id=request.user.id)
        serializer = MessengerUsersSerializer(users, many=True)
        return Response({'msg': 'All user data excluding the current user', 'data': serializer.data}, status=status.HTTP_200_OK)



#Have to work on Message filter  
class ChatMessengerApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        receiver = User.objects.get(name=username)
        users    = User.objects.exclude(name=username)

        if request.user.id > receiver.id:
            thread_name = f'chat_{request.user.id}-{receiver.id}'
        else:
            thread_name = f'chat_{receiver.id}-{request.user.id}'

        msg = ChatModel.objects.filter(thread_name=thread_name)

        serializer = ChatModelSerializer(msg, many=True)
        users_serializer = MessengerUsersSerializer(users, many=True)
        receiver_serializer = MessengerUsersSerializer(receiver)

        response_data = {
            "Message": serializer.data,
            "All users": users_serializer.data,
            "Receiver": receiver_serializer.data
        }

        return Response({'msg': 'Success', 'data': response_data})


# def home_view(request):
#     users = User.objects.exclude(id=request.user.id)
#     return render(request, 'messenger/home.html', context={'users': users})


# def chatpage(request, username):
#     receiver = User.objects.get(name=username)
#     users    = User.objects.exclude(name=username)

#     if request.user.id > receiver.id:
#         thread_name = f'chat_{request.user.id}-{receiver.id}'
#     else:
#         thread_name = f'chat_{receiver.id}-{request.user.id}'

#     message_objs = ChatModel.objects.filter(thread_name=thread_name)
#     print(message_objs)
#     return render(request, 'messenger/chat.html', context={'receiver': receiver, 'users': users, 'messages': message_objs})

