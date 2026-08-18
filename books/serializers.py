from rest_framework import serializers

from .models import Category, Author, Publisher, Book, BookImage


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]


class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Author
        fields = ["id", "name", "slug", "bio", "photo"]


class PublisherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Publisher
        fields = ["id", "name"]


class BookImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookImage
        fields = ["id", "image", "alt_text"]


class BookListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for catalog / search listing pages."""

    authors = AuthorSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "slug",
            "authors",
            "category",
            "price",
            "cover_image",
            "format",
            "in_stock",
            "is_featured",
        ]


class BookDetailSerializer(serializers.ModelSerializer):

    authors = AuthorSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    images = BookImageSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "slug",
            "authors",
            "category",
            "publisher",
            "isbn",
            "description",
            "price",
            "stock",
            "in_stock",
            "cover_image",
            "images",
            "format",
            "language",
            "pages",
            "published_date",
            "is_featured",
            "created_at",
            "updated_at",
        ]