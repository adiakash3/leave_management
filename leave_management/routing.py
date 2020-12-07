from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path 
from leave_management.channels_token_auth import TokenAuthMiddlewareStack
from push_notifications.consumer import MessageConsumer

application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter([
            path("ws/notifications", MessageConsumer),
        ])
    ),

})