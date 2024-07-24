# serializers.py

from rest_framework import serializers
from .models import ChatMessage, Room


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["sender", "receiver", "message", "timestamp"]


class RoomSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["other_user"]

    def get_other_user(self, obj):
        if obj.user1 == self.context["request"].user.username:
            return obj.user2
        else:
            return obj.user1
