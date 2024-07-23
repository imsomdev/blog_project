from django.urls import path
from chat.consumers import ChatConsumer

websocket_url = [
    path("ws/chat/<str:user1>/<str:user2>/", ChatConsumer.as_asgi()),
]
