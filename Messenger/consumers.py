import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from Messenger.models import ChatModel, ChatNotification, UserProfileModel
from users.models import User


class PersonalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        sender_id = self.scope['user'].id
        receiver_id = self.scope['url_route']['kwargs']['id']

        if int(sender_id) > int(receiver_id):
            self.room_name = f'{sender_id}--{receiver_id}'
        else:
            self.room_name = f'{receiver_id}--{sender_id}'

        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()


    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data['message']
        sender = data['sender']
        receiver = data['receiver']

        await self.save_message(sender, self.room_group_name, message, receiver)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
            }
        )


    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': sender
        }))

    async def disconnect(self, code):
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    

    @database_sync_to_async
    def save_message(self, sender, thread_name, message, receiver):

        if sender == receiver:
            response = json.dumps({'msg': 'sender and receiver are the same'})
            return response
        
        chat_obj = ChatModel.objects.create(
            sender=sender, message=message, thread_name=thread_name, receiver= receiver
        )
        receiver_id = self.scope['url_route']['kwargs']['id']
        get_user    = User.objects.get(id=receiver_id)

        if receiver == get_user.name:
            ChatNotification.objects.create(chat=chat_obj, user=get_user)
      

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        my_id = self.scope['user'].id
        self.room_group_name = f'{my_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, code):
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        data = json.loads(event.get('value'))
        count = data['count']

        await self.send(text_data=json.dumps({
            'count':count
        }))


        
class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'user'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        username = data['username']
        connection_type = data['type']
        print(connection_type)

        await self.change_online_status(username, connection_type)

    async def send_onlineStatus(self, event):
        data = json.loads(event.get('value'))
        username = data['username']
        online_status = data['status']
        await self.send(text_data=json.dumps({
            'username':username,
            'online_status':online_status
        }))


    async def disconnect(self, message):
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    @database_sync_to_async
    def change_online_status(self, username, c_type):
        user = User.objects.get(username=username)
        userprofile = UserProfileModel.objects.get(user=user)
        if c_type == 'open':
            userprofile.online_status = True
            userprofile.save()
        else:
            userprofile.online_status = False
            userprofile.save()