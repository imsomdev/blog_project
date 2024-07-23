import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer


class MyConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = "test_server"

    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)(self.room_name, self.channel_name)

    def receive_json(self, content=None):
        """
        This method receives JSON messages from WebSocket and forwards them to the group.
        """
        try:
            message = content.get("message")
            if message:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_name,
                    {
                        "type": "chat.message",
                        "new_message": message,
                    },
                )
        except Exception as e:
            # Handle any unexpected errors
            self.send_json({"error": str(e)})

    def chat_message(self, event):
        """
        This method sends the message to WebSocket.
        """
        self.send_json(event)

    def disconnect(self, close_code):
        """
        This method handles the disconnection and leaves the group.
        """
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name, self.channel_name
        )
