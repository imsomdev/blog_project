from django.urls import path
from .views import UserRegistrationView, UserLoginView, BlogContentView

urlpatterns = [
    path('register', UserRegistrationView.as_view(), name='UserRegistrationView'),
    path('login', UserLoginView.as_view(), name='UserLoginView'),
    path('create-blog', BlogContentView.as_view(), name='BlogContentView')
]
