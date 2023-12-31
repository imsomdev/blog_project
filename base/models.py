from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class BlogContent(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
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
    bio = models.CharField(max_length=150, blank=True)
    address = models.CharField(max_length=255)
    pin = models.CharField(max_length=6)
    ph_no = models.CharField(max_length=10)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
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
        return self.user.username


class BlogPostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogContent, on_delete=models.CASCADE, related_name='like')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.title

