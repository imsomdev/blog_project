from django.contrib import admin
from .models import BlogContent, UserProfile, UserComment, BlogPostLike
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.
admin.site.register(BlogContent, SimpleHistoryAdmin)
admin.site.register(UserProfile, SimpleHistoryAdmin)
admin.site.register(UserComment)
admin.site.register(BlogPostLike)


