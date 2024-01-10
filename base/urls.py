from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import BlogPostLikeView, UserRegistrationView, UserLoginView, BlogContentView, BlogContentListView,UserProfileView, UserCommentView, DynamicSearchView, FilterRecentPostView, PopularPostsView

schema_view = get_schema_view(
    openapi.Info(
        title="My Blog",
        default_version='v1',
        description="Your API description",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('register', UserRegistrationView.as_view(), name='UserRegistrationView'),
    path('login', UserLoginView.as_view(), name='UserLoginView'),
    path('create-post', BlogContentView.as_view(), name='BlogContentView'),
    path('blog-posts', BlogContentListView.as_view(), name='BlogContentListView'),
    path('blog-posts/<int:pk>', BlogContentListView.as_view(), name='BlogContentListView'), # For deleting 
    path('profile', UserProfileView.as_view(), name='UserProfileView'),
    path('profile/<str:username>', UserProfileView.as_view(), name='UserProfileViewPublic'),
    path('blog-posts/<int:pk>/comment', UserCommentView.as_view(), name = 'UserCommentView'),
    path('blog-posts/<int:pk>/like', BlogPostLikeView.as_view(), name='BlogPostLikeView'),
    path('search', DynamicSearchView.as_view(), name='DynamicSearchView'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('recent-posts', FilterRecentPostView.as_view(), name='FilterRecentPostView'),
    path('popular-post', PopularPostsView.as_view(), name='PopularPostsView'),
]
