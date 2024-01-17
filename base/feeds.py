from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import BlogContent


class BlogContentFeed(Feed):
    title = "Latest Blog Posts"
    link = "/blogs/"
    description = "Latest blog posts"

    def items(self):
        return BlogContent.objects.order_by("-created_at")[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content
    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return reverse("BlogContentListView", args=[item.pk])