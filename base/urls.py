from django.urls import path
from .views import UserRegistrationView, UserLoginView, BlogContentView, BlogContentListView,UserProfileView

urlpatterns = [
    path('register', UserRegistrationView.as_view(), name='UserRegistrationView'),
    path('login', UserLoginView.as_view(), name='UserLoginView'),
    path('create-post', BlogContentView.as_view(), name='BlogContentView'),
    path('blog-posts', BlogContentListView.as_view(), name='BlogContentListView'),
    path('blog-posts/<int:pk>/', BlogContentListView.as_view(), name='BlogContentListView'), # For deleting 
    path('profile', UserProfileView.as_view(), name='UserProfileView'),
    path('profile/update', UserProfileView.as_view(), name='UserProfileViewUpdate')
]
