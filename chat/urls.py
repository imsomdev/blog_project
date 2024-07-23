# urls.py

from django.urls import path
from .views import ChatHistoryView

urlpatterns = [
    path(
        "chat/history/<str:user1>/<str:user2>/",
        ChatHistoryView.as_view(),
        name="chat_history",
    ),
]
