from rest_framework.pagination import PageNumberPagination


class BlogContentPagination(PageNumberPagination):
    page_size = 2
