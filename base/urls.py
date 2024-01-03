from django.urls import path
from .views import BlogPostLikeView, UserRegistrationView, UserLoginView, BlogContentView, BlogContentListView,UserProfileView, UserCommentView

urlpatterns = [
    path('register', UserRegistrationView.as_view(), name='UserRegistrationView'),
    path('login', UserLoginView.as_view(), name='UserLoginView'),
    path('create-post', BlogContentView.as_view(), name='BlogContentView'),
    path('blog-posts', BlogContentListView.as_view(), name='BlogContentListView'),
    path('blog-posts/<int:pk>', BlogContentListView.as_view(), name='BlogContentListView'), # For deleting 
    path('profile', UserProfileView.as_view(), name='UserProfileView'),
    path('profile/update', UserProfileView.as_view(), name='UserProfileViewUpdate'),
    path('profile/<str:username>', UserProfileView.as_view(), name='UserProfileViewPublic'),
    path('blog-posts/<int:pk>/comment', UserCommentView.as_view(), name = 'UserCommentView'),
    path('blog-posts/<int:pk>/like', BlogPostLikeView.as_view(), name='BlogPostLikeView'),
]
