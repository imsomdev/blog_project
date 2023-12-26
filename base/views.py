# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer, UserLoginSerializer, BlogContentSerializer, BlogContentListSerializer
from .models import BlogContent

class UserRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
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
        # Perform any additional actions for login if needed
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
    def get(self, request):
        blogs = BlogContent.objects.all()
        serializer = BlogContentListSerializer(blogs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

