import random
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import BlogContent, UserProfile, UserComment, BlogPostLike, Tag, Follow
from django.core.files.base import ContentFile
from pathlib import Path

def generate_default_profile_picture(gender):
    # List of paths to default profile pictures based on gender
    male_default_pictures = [
        '/media/somdev/84AE09BCAE09A82E/Programs/Programs and Frameworks/Django/blog_project/user_profiles/00.DefaultProfilePicture/man-user-circle-icon.png',
        # Add more paths as needed
    ]

    female_default_pictures = [
        '/media/somdev/84AE09BCAE09A82E/Programs/Programs and Frameworks/Django/blog_project/user_profiles/00.DefaultProfilePicture/woman-user-circle-icon.png',
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
    

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']

class BlogContentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = BlogContent
        fields = ['title', 'content', 'image', 'author', 'tags']


    def get_author(self, obj):
        return obj.author.username
    
    # BOTH FUNCTIONS  ARE FOR TAG FIELD
    def to_internal_value(self, data):
        tags_data = data.get('tags', [])
        data = super().to_internal_value(data)
        data['tags'] = tags_data
        return data

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        instance = super().create(validated_data)
        if tags_data:
            instance.tags.set(tags_data)
        return instance
    


class BlogContentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogContent
        fields = ['title']

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = '__all__'


    def get_followers_count(self, obj):
        return Follow.objects.filter(following=obj.user).count()

    def get_following_count(self, obj):
        return Follow.objects.filter(follower=obj.user).count()
    
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
            raise serializers.ValidationError('Profile picture size must be under 1 MB.')
        return value

    def set_default_profile_picture(self, validated_data):
        if 'profile_picture' not in validated_data or validated_data['profile_picture'] is None:
            gender = validated_data.get('gender', 'U')
            if 'profile_picture' not in self.initial_data:
                default_profile_picture_path = generate_default_profile_picture(gender)
                with open(default_profile_picture_path, 'rb') as file:
                    content = file.read()
                    file_extension = Path(default_profile_picture_path).suffix
                    default_picture_name = f'default_profile_picture{file_extension}'

                    default_picture = ContentFile(content, name=default_picture_name)
                    validated_data['profile_picture'] = default_picture

    def update(self, instance, validated_data):
        profile = UserProfile.objects.get(user_id=instance.user_id)
        profile_picture = profile.profile_picture
        if 'profile_picture' in validated_data:
            profile_picture = validated_data['profile_picture']
        if not profile_picture:
            self.set_default_profile_picture(validated_data)
        return super().update(instance, validated_data)
    
class UserCommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = UserComment
        fields = ['user', 'comment']
        
    def get_user(self, obj):
        return obj.user.username
    
class BlogPostLikeSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = BlogPostLike
        fields = ['user']

    def get_user(self, obj):
            return obj.user.username

from rest_framework import serializers

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['follower', 'following', 'created_at']

    def to_representation(self, instance):
        method = self.context['request'].method

        if method == 'GET':
            return {
                'follower_name': instance.follower.username,
                'following_name': instance.following.username,
            }
        elif method == 'POST':
            return super().to_representation(instance)
