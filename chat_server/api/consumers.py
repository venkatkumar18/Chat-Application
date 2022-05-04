import json

from channels.generic.websocket import AsyncWebsocketConsumer # The class we're using
from asgiref.sync import sync_to_async # Implement later
from django.contrib.auth.models import User
from .models import Chat,Chat_table
from django.utils import timezone
from . import get_id
class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Join room based on name in the URL
        self.room_name = self.scope['url_route']['kwargs']['room']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        room = data['room']
        await self.save_message(username, room, message)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @sync_to_async
    def save_message(self, username, room, message):
        user = Chat()
        if(room==1000):
            index = 1000
        else:
            index = get_id.get_write_id()
        user.id = index
        user.message = message
        user.chatRoom = str(room)
        if(room==1000):
            user.fromEmail = username
            user.toEmail = ''
            user.createdDatetime = timezone.now()
            user.save()
        else:
            obj = Chat_table.objects.get(chatRoom=int(room))
            user.createdDatetime = obj.initiatedDateTime
            if(obj.participantEmail==username):
                user.fromEmail = obj.participantEmail
                user.toEmail = obj.hostEmail
            elif(obj.hostEmail==username):
                user.fromEmail = obj.hostEmail
                user.toEmail = obj.participantEmail
            else:
                user.fromEmail = username
                user.toEmail = ''
            user.save()




