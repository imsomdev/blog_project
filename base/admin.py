from django.contrib import admin
from .models import BlogContent, UserProfile, UserComment, BlogPostLike, Tag, Follow, SavedPost, Choice, Question
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.
admin.site.register(BlogContent, SimpleHistoryAdmin)
admin.site.register(UserProfile, SimpleHistoryAdmin)
admin.site.register(UserComment)
admin.site.register(BlogPostLike)
admin.site.register(Tag)
admin.site.register(Follow)
admin.site.register(SavedPost)
admin.site.register(Choice)
admin.site.register(Question)




