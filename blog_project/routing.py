from django.urls import path
from chat.consumers import ChatConsumer, ChatListConsumer

websocket_url = [
    path("ws/chat/<str:user1>/<str:user2>", ChatConsumer.as_asgi()),
    path("ws/notification/chat/<str:user>", ChatListConsumer.as_asgi()),
]
