from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from .models import ChatMessage


class ChatConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.user1 = self.scope["url_route"]["kwargs"]["user1"]
        self.user2 = self.scope["url_route"]["kwargs"]["user2"]
        self.room_name = (
            f"{self.user1}-{self.user2}"
            if self.user1 < self.user2
            else f"{self.user2}-{self.user1}"
        )
        self.room_group_name = f"chat_{self.room_name}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive_json(self, content):
        message = content.get("message")
        sender = content.get("sender")
        receiver = self.user2 if sender == self.user1 else self.user1
        ChatMessage.objects.create(sender=sender, receiver=receiver, message=message)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender,
            },
        )

    def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]

        self.send_json(
            {
                "message": message,
                "sender": sender,
            }
        )
