from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters
from .serializers import UserRegistrationSerializer, UserLoginSerializer, BlogContentSerializer, BlogContentListSerializer, UserProfileSerializer, UserCommentSerializer, BlogPostLikeSerializer, FollowSerializer,SavedPostSerializer
from .models import BlogContent, UserProfile, UserComment, BlogPostLike, Follow, SavedPost
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Count, F


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
        responses={201: BlogContentSerializer, 
                   400: 'Bad Request', 
                   401: 'Unauthorized'}
    )
    def post(self, request):
        request.data._mutable = True
        tag_ids = request.data.get('tags')
        tag_ids_int = [int(i) for i in tag_ids.split(',')]
        request.data['tags'] = tag_ids_int
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
            return Response({'detail': 'Post Deleted!'}, status=status.HTTP_204_NO_CONTENT)
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

    # @swagger_auto_schema(
    #     request_body=UserProfileSerializer,
    #     responses={201: UserProfileSerializer}
    # )
    # def post(self, request):
    #     existing_user = UserProfile.objects.filter(user=request.user).first()
    #     if existing_user:
    #         return Response({'detail': 'User Profile Already Exists, Use Update to make'})
    #     serializer = UserProfileSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save(user=request.user)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=UserProfileSerializer,
        responses={201: UserProfileSerializer}
    )
    def patch(self, request):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)

        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
class UserCommentView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        responses={200: UserCommentSerializer}
    )
    def get(self, request, pk):
        try:
            blog_post = BlogContent.objects.get(id=pk)
        except BlogContent.DoesNotExist:
            return Response({"error": "Blog post not found"}, status=status.HTTP_404_NOT_FOUND)
        comment = blog_post.usercomment_set.all()
        serializer = UserCommentSerializer(comment, many=True)
        return Response (serializer.data)


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
    def get(self, request, pk):
        try:
            blog_post = BlogContent.objects.get(pk=pk)
        except BlogContent.DoesNotExist:
            return Response({"error": "Blog post not found"}, status=status.HTTP_404_NOT_FOUND)
        likes = blog_post.like.all()
        serializer = BlogPostLikeSerializer(likes, many=True)
        return Response(serializer.data)

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
            

class DynamicSearchView(generics.ListAPIView):
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
    

class FilterRecentPostView(generics.ListAPIView):
    queryset = BlogContent.objects.order_by('-created_at')
    serializer_class = BlogContentSerializer
    

class PopularPostsView(APIView):
    def get(self, request):
        posts_with_counts = BlogContent.objects.annotate(
            like_count=Count('likes'),
        )
        popularity_score = F('like_count')
        ordered_posts = posts_with_counts.order_by(-popularity_score)
        serializer = BlogContentSerializer(ordered_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TopAuthorsView(APIView):
    def get(self, request):
        authors_with_post_counts = UserProfile.objects.annotate(
            total_posts=Count('user__posts')
        )
        ordered_authors = authors_with_post_counts.order_by('-total_posts')[:5]
        serializer = UserProfileSerializer(ordered_authors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UsersPostView(APIView):
    def get(self, request, username):
        print(request)
        user = User.objects.get(username=username)
        users_posts = user.posts.all()
        serializer = BlogContentListSerializer(users_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = User.objects.get(username=request.user.username)
        following = user.following_set.all()
        followers = user.followers_set.all()
        serializer = FollowSerializer(following, many=True, context={'request': request})
        serializer_2 = FollowSerializer(followers, many=True, context={'request': request})
        return Response({
                        "following": [data['following_name'] for data in serializer.data],
                        "followers": [data['follower_name'] for data in serializer_2.data]
                        }
                       )
    
    @swagger_auto_schema(
        responses={
            200: "Unfollowed successfully",
            201: "Followed successfully",
            400: "Bad Request",
            401: "Unauthorized",
            404: "User not found",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        )
    )
    def post(self, request):
        user_to_follow_id = request.data.get('user_id')
        user_to_follow = User.objects.get(id=user_to_follow_id)
        if request.user == user_to_follow:
            return Response({'detail': 'You cannot follow/unfollow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            follow_instance = Follow.objects.get(follower=request.user, following=user_to_follow)
            follow_instance.delete()
            serializer = FollowSerializer(follow_instance)
            return Response({'detail': f'You have unfollowed {user_to_follow.username}.'}, status=status.HTTP_200_OK)
        
        except Follow.DoesNotExist:
            follow_instance = Follow.objects.create(follower=request.user, following=user_to_follow)
            serializer = FollowSerializer(follow_instance, context={'request': request})
            return Response({'detail': f'You are now following {user_to_follow.username}.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        

class FilterByTagsView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'tags',
                openapi.IN_QUERY,
                description="Tag ID as a string",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: BlogContentSerializer(many=True)},
    )
    def get(self, request):
        try:
            tag_id = int(request.query_params.get('tags'))
        except (TypeError, ValueError):
            return Response({"error": "Invalid or missing tag ID"}, status=400)
        posts = BlogContent.objects.filter(tags=tag_id)
        serializer = BlogContentSerializer(posts, many=True)
        return Response(serializer.data)
    

class SavedPostView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        user = User.objects.get(id=request.user.id)
        posts = user.saved_posts.all()
        # blog_posts = BlogContent.objects.filter(id=posts.post_id)
        serializer = SavedPostSerializer(posts, many=True)
        return Response(serializer.data)
    @swagger_auto_schema(
        responses={
            200: "Post Unsaved",
            201: "Post Saved",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Post Not Found",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        )
    )
    def post(self, request):
        try:
            post = BlogContent.objects.get(id=request.data.get('post_id'))
        except(BlogContent.DoesNotExist):
            return Response({"details": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        saved_post = SavedPost.objects.filter(user=request.user.id, post=post).first()
        if saved_post:
            saved_post.delete()
            return Response({"details": "Post Unsaved"}, status=status.HTTP_200_OK)
        else:
            saved_data = {'user': request.user.id, 'post': post.id}
            serialzer = SavedPostSerializer(data=saved_data)
            if serialzer.is_valid():
                serialzer.save()
                return Response({"details": "Post Saved"}, status=status.HTTP_201_CREATED)