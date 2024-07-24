from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ChatMessage, Room
from django.db.models import Q
from .serializers import ChatMessageSerializer, RoomSerializer


class ChatHistoryView(APIView):
    def get(self, request, user1, user2):
        room_name = f"{user1}-{user2}" if user1 < user2 else f"{user2}-{user1}"
        messages = ChatMessage.objects.filter(
            (Q(sender=user1) & Q(receiver=user2))
            | (Q(sender=user2) & Q(receiver=user1))
        ).order_by("timestamp")
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)


class GetUserRoomsAPIView(APIView):
    def get(self, request):
        username = request.user.username
        rooms = Room.objects.filter(Q(user1=username) | Q(user2=username))
        serializer = RoomSerializer(rooms, many=True, context={"request": request})
        return Response(serializer.data)
