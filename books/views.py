from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Author, Book
from .serializers import (
    CategorySerializer,
    AuthorSerializer,
    BookListSerializer,
    BookDetailSerializer,
)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class AuthorListView(generics.ListAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookListView(generics.ListAPIView):
    """
    Public catalog listing. Supports:
    - ?search=<title/author/isbn>
    - ?category=<slug>
    - ?author=<slug>
    - ?format=paperback|hardcover|ebook
    - ?ordering=price,-price,-created_at
    """

    serializer_class = BookListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "category__slug": ["exact"],
        "authors__slug": ["exact"],
        "format": ["exact"],
        "price": ["gte", "lte"],
    }
    search_fields = ["title", "isbn", "authors__name"]
    ordering_fields = ["price", "created_at", "title"]

    def get_queryset(self):
        return Book.objects.filter(is_active=True).distinct()


class FeaturedBookListView(generics.ListAPIView):
    serializer_class = BookListSerializer

    def get_queryset(self):
        return Book.objects.filter(is_active=True, is_featured=True)


class BookDetailView(generics.RetrieveAPIView):
    serializer_class = BookDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Book.objects.filter(is_active=True)