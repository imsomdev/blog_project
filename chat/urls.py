# urls.py

from django.urls import path
from .views import ChatHistoryView, GetUserRoomsAPIView

urlpatterns = [
    path(
        "chat/history/<str:user1>/<str:user2>/",
        ChatHistoryView.as_view(),
        name="chat_history",
    ),
    path("get-user-rooms/", GetUserRoomsAPIView.as_view()),
]
