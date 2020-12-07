
from channels.auth import login
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import *
import json


class MessageConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        print("connect")
        # Are they logged in?
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
        else:
            #Accept the connection
            await self.accept()
        # await login(self.scope, self.scope["user"])
        self.user = self.scope["user"]
        self.one_to_one_group_name = ('notification-to-{}'.format(self.user.email)).replace('_','-').replace('@','').replace('+','')
        self.broadcast_group_name = 'broadcast'
        try:
            await self.channel_layer.group_add(self.broadcast_group_name, self.channel_name)
            await self.channel_layer.group_add(self.one_to_one_group_name, self.channel_name)
        except Exception as e:
            print('Error while connetecting to wb ', e)
        

        print("Added {} channel to notification".format(self.channel_name))
        

    async def disconnect(self, close_code):
        print("disconnect")
        await self.channel_layer.group_discard(self.broadcast_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.one_to_one_group_name, self.channel_name)
        
        print(" removed {} channel to notification".format(self.channel_name))
    
    # Receive message from room_group
    # this method get no of times called based on the number of connection 
    async def user_message(self, event):
        print("user_message")
        message = event['message']
       
        # await self.send_notification(message)
         
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
        print("got message {} at {}".format(event, self.channel_name))

