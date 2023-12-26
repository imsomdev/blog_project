from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import BlogContent

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
    class Meta:
        model = BlogContent
        fields = '__all__'
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return obj.author.username
