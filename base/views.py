from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters
from .serializers import UserRegistrationSerializer, UserLoginSerializer, BlogContentSerializer, BlogContentListSerializer, UserProfileSerializer, UserCommentSerializer, BlogPostLikeSerializer
from .models import BlogContent, UserProfile, UserComment, BlogPostLike 
from django.contrib.auth.models import User
class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response({'username': user.username}, status=status.HTTP_200_OK)
    

class BlogContentView(APIView):
    def post(self, request):
        serializer = BlogContentSerializer(data=request.data)
        if serializer.is_valid():
            # Assuming you have user authentication in place
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlogContentListView(APIView):
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
            return Response({'detail': 'You do not have permission to update this blog post.'},status=status.HTTP_403_FORBIDDEN)
        
    # To delete a blog post using pk
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
    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            print(user)
            user_profile = UserProfile.objects.get(user=user)
            print(user_profile)
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data)
        except User.DoesNotExist:
            raise Http404
        except UserProfile.DoesNotExist:
            raise Http404

    def post(self, request):
        existing_user = UserProfile.objects.filter(user=request.user).first()
        if existing_user:
            return Response({'detail': 'User Profile Alreday Exists, Use Update to make'})
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        existing_user = UserProfile.objects.filter(user=request.user).first()
        if not existing_user:
            return Response ({'Profile not created, use POST to first create profile'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(existing_user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
class UserCommentView(APIView):
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return Response({'error': 'Please login first'}, status=status.HTTP_401_UNAUTHORIZED)
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
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return Response({'error': 'Please login first'}, status=status.HTTP_401_UNAUTHORIZED)
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

