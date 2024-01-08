import random
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import BlogContent, UserProfile, UserComment, BlogPostLike
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def generate_default_profile_picture(gender):
    # List of paths to default profile pictures based on gender
    male_default_pictures = [
        '/media/somdev/84AE09BCAE09A82E/Programs/Programs and Frameworks/Django/blog_project/user_profiles/00.DefaultProfilePicture/M_Default.webp',
        # Add more paths as needed
    ]

    female_default_pictures = [
        '/media/somdev/84AE09BCAE09A82E/Programs/Programs and Frameworks/Django/blog_project/user_profiles/00.DefaultProfilePicture/F_Default.webp',
        # Add more paths as needed
    ]

    # Select a random path based on gender
    if gender == 'M':
        return random.choice(male_default_pictures)
    else:
        return random.choice(female_default_pictures)
    

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if user and user.is_active:
                data['user'] = user
            else:
                raise serializers.ValidationError("Incorrect credentials. Please try again.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")

        return data
    

class BlogContentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = BlogContent
        # fields = '__all__'
        fields = ['title', 'content', 'author', 'tags']

    def get_author(self, obj):
        return obj.author.username


class BlogContentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogContent
        fields = ['title']

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = '__all__'

    def get_user(self, obj):
        return obj.user.username
    
    def validate_ph_no(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only numeric characters.")
        return value

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("PIN must contain only numeric characters.")
        return value
    
    def validate_profile_picture(self, value):
        max_size = 1 * 1024 * 1024  # 1 MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError('Profile picture size must be under 2MB.')
        return value

    def create(self, validated_data):
        gender = validated_data.get('gender', 'U')

        # Check if profile picture is not provided or is set to None
        if 'profile_picture' not in validated_data or validated_data['profile_picture'] is None:
            default_profile_picture_path = generate_default_profile_picture(gender)

            # Save the default image to the storage
            with open(default_profile_picture_path, 'rb') as file:
                content = file.read()
                default_picture = ContentFile(content, name='default_profile_picture.jpg')
                validated_data['profile_picture'] = default_picture

        return super().create(validated_data)
    
class UserCommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = UserComment
        fields = ['user', 'comment']
        
    def get_user(self, obj):
        return obj.user.username
    
class BlogPostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPostLike
        fields = ['user', 'post', 'created_at']