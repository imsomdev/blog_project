from django.db import models


class Room(models.Model):
    user1 = models.CharField(max_length=255)
    user2 = models.CharField(max_length=255)
    room_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.room_name


class ChatMessage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} in {self.room.room_name} at {self.timestamp}"
