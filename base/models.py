import datetime
from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from django.utils import timezone


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
def blog_content_image_path(instance, filename):
    # Define the file path for storing profile pictures
    return f'user_profiles/{instance.author.username}/blog_image/{filename}'

class BlogContent(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to=blog_content_image_path, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, through='BlogPostLike', related_name='liked_posts')
    history = HistoricalRecords()

    def __str__(self):
        return self.title
    

def profile_picture_path(instance, filename):
    # Define the file path for storing profile pictures
    return f'user_profiles/{instance.user.username}/profile_picture/{filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=150, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    pin = models.CharField(max_length=6, blank=True, null=True)
    ph_no = models.CharField(max_length=10, blank=True, null=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    profile_picture = models.ImageField(upload_to=profile_picture_path, blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.user.username
    

class UserComment(models.Model):
    comment = models.TextField()
    post = models.ForeignKey(BlogContent, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.post.title


class BlogPostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogContent, on_delete=models.CASCADE, related_name='like')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.title
    

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')
    

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'
    

class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(BlogContent, on_delete=models.CASCADE, related_name='saved_users')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.title


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return self.choice_text
 

class Voters(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    voters = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.voters.username


class Pro(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_pro = models.BooleanField()

    def __str__(self):
        return self.user.username