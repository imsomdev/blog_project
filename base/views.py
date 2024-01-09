from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters
from .serializers import UserRegistrationSerializer, UserLoginSerializer, BlogContentSerializer, BlogContentListSerializer, UserProfileSerializer, UserCommentSerializer, BlogPostLikeSerializer
from .models import BlogContent, UserProfile, UserComment, BlogPostLike 
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

class UserRegistrationView(APIView):
    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
        responses={201: UserRegistrationSerializer}
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer

    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={200: UserLoginSerializer}
    )
    def post(self, request):
        user = User.objects.get(username=request.data['username'])
        if not user.check_password(request.data['password']):
            return Response('Invalid credentials', status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({'refresh': str(refresh), 'jwt': str(refresh.access_token)})
    

class BlogContentView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=BlogContentSerializer,
        responses={201: BlogContentSerializer, 400: 'Bad Request', 401: 'Unauthorized'}
    )
    def post(self, request):
        serializer = BlogContentSerializer(data=request.data)
        if serializer.is_valid():
            # Assuming you have user authentication in place
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlogContentListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        responses={200: BlogContentSerializer(many=True)}
    )
    def get(self, request, pk=None):
        if pk is not None:
            try:
                blog_post = BlogContent.objects.get(pk=pk)
                serializer = BlogContentSerializer(blog_post)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except BlogContent.DoesNotExist:
                raise Http404
        else:
            blogs = BlogContent.objects.all()
            serializer = BlogContentListSerializer(blogs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=BlogContentSerializer,
        responses={200: BlogContentSerializer, 400: 'Bad Request', 403: 'Forbidden'}
    )
    def put(self, request, pk):
        try:
            blog_post = BlogContent.objects.get(pk=pk)
        except BlogContent.DoesNotExist:
            raise Http404

        if blog_post.author == request.user or request.user.is_staff:
            serializer = BlogContentSerializer(blog_post, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'You do not have permission to update this blog post.'}, status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(
        responses={204: 'No Content', 403: 'Forbidden'}
    )
    def delete(self, request, pk):
        try:
            blog_post = BlogContent.objects.get(pk=pk)
        except BlogContent.DoesNotExist:
            raise Http404

        if blog_post.author == request.user or request.user.is_staff:
            blog_post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'You do not have permission to delete this blog post.'}, status=status.HTTP_403_FORBIDDEN)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    @swagger_auto_schema(
        responses={200: UserProfileSerializer}
    )
    def get(self, request, username=None):
        if not request.user.is_authenticated:
            return Response({'detail': 'Please log in to view profiles'}, status=status.HTTP_401_UNAUTHORIZED)
        if username is not None:
            try:
                user = User.objects.get(username=username)
                user_profile = UserProfile.objects.get(user=user)
                serializer = UserProfileSerializer(user_profile)
                return Response(serializer.data)
            except User.DoesNotExist:
                raise Http404
            except UserProfile.DoesNotExist:
                raise Http404
        else:
            # Return the profile of the authenticated user
            user_profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data)

    @swagger_auto_schema(
        request_body=UserProfileSerializer,
        responses={201: UserProfileSerializer}
    )
    def post(self, request):
        existing_user = UserProfile.objects.filter(user=request.user).first()
        if existing_user:
            return Response({'detail': 'User Profile Already Exists, Use Update to make'})
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=UserProfileSerializer,
        responses={201: UserProfileSerializer}
    )
    def put(self, request):
        existing_user = UserProfile.objects.filter(user=request.user).first()
        if not existing_user:
            return Response({'detail': 'Profile not created, use POST to first create profile'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(existing_user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
class UserCommentView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserCommentSerializer,
        responses={201: UserCommentSerializer, 
                   400: 'Bad Request', 
                   401: 'Unauthorized', 
                   404: 'Blog post not found'
        }
    )
    def post(self, request, pk):
        try:
            blog_post = BlogContent.objects.get(pk=pk)
        except BlogContent.DoesNotExist:
            return Response({"error": "Blog post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=blog_post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class BlogPostLikeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: "Post disliked successfully",
            201: "Post liked successfully",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Blog post not found",
        }
    )
    def post(self, request, pk):
        try:
            blog_post = BlogContent.objects.get(pk=pk)
        except BlogContent.DoesNotExist:
            return Response({"error": "Blog post not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has already liked the post
        existing_like = BlogPostLike.objects.filter(user=request.user, post=blog_post).first()

        if existing_like:
            # User has already liked the post, so dislike it
            existing_like.delete()
            return Response({'message': 'Post disliked successfully'}, status=status.HTTP_200_OK)
        else:
            # User has not liked the post, so like it
            like_data = {'user': request.user.id, 'post': blog_post.id}
            serializer = BlogPostLikeSerializer(data=like_data)

            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Post liked successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

class DynamicSearch(generics.ListAPIView):
    queryset = BlogContent.objects.all()
    serializer_class = BlogContentSerializer
    search_fields = ['content', 'title']
    filter_backends = (filters.SearchFilter,)

    @swagger_auto_schema(
        responses={200: BlogContentSerializer(many=True),
                   404: 'Not Found'}
    )
    def get_queryset(self):
        search_param = self.request.query_params.get('search', None)
        if not search_param:
            return BlogContent.objects.none()
        queryset = BlogContent.objects.filter(content__icontains=search_param) | BlogContent.objects.filter(title__icontains=search_param)
        return queryset
    
    def list(self, request):
        queryset = self.get_queryset()
        serializer = BlogContentSerializer(queryset, many=True)
        if not queryset.exists():
            return Response({'message': 'Please provide some valid search input'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)

