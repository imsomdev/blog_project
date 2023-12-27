from django.contrib import admin
from .models import BlogContent
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.
admin.site.register(BlogContent, SimpleHistoryAdmin)