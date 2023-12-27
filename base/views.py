from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer, UserLoginSerializer, BlogContentSerializer, BlogContentListSerializer
from .models import BlogContent


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
            serializer.save(author=request.user) ## Here it's authenticating
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

