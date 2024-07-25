from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from .models import Room, ChatMessage


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
        self.notification_group_name = f"notification_{self.user2}"

        # Join the room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave the room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive_json(self, content):
        message = content.get("message")
        sender = content.get("sender")
        receiver = self.user2 if sender == self.user1 else self.user1

        # Create the room only if it doesn't exist when a message is sent
        room, created = Room.objects.get_or_create(room_name=self.room_name)
        if created:
            room.user1 = self.user1
            room.user2 = self.user2
            room.save()

        ChatMessage.objects.create(
            room=room, sender=sender, receiver=receiver, message=message
        )

        # Send the message to the room group
        async_to_sync(self.channel_layer.group_send)(
            self.notification_group_name,
            {
                "type": "chat_notification",
                "message": message,
                "sender": sender,
            },
        )

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

        # Send the message to WebSocket
        self.send_json(
            {
                "message": message,
                "sender": sender,
            }
        )

    def chat_notification(self, event):
        sender = event["sender"]

        # Send the message to WebSocket
        self.send_json(
            {
                "type": "chat_notification",
                "sender": sender,
            }
        )


class ChatListConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.user = self.scope["url_route"]["kwargs"]["user"]
        self.notification_group_name = f"notification_{self.user}"
        async_to_sync(self.channel_layer.group_add)(
            self.notification_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.notification_group_name, self.channel_name
        )

    def chat_notification(self, event):
        sender = event["sender"]

        # Send the notification to WebSocket
        self.send_json(
            {
                "type": "chat_notification",
                "sender": sender,
            }
        )
