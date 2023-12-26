from django.urls import path
from .views import UserRegistrationView, UserLoginView, BlogContentView, BlogContentListView

urlpatterns = [
    path('register', UserRegistrationView.as_view(), name='UserRegistrationView'),
    path('login', UserLoginView.as_view(), name='UserLoginView'),
    path('create-blog', BlogContentView.as_view(), name='BlogContentView'),
    path('blogs', BlogContentListView.as_view(), name='BlogContentListView')
]
