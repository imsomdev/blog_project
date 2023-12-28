from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import BlogContent, UserProfile

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
    # author = serializers.SerializerMethodField()

    class Meta:
        model = BlogContent
        # fields = '__all__'
        fields = ['title', 'content']

    # def get_author(self, obj):
    #     return obj.author.username


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