from django.urls import path
from .views import (
    CategoryListView,
    AuthorListView,
    BookListView,
    FeaturedBookListView,
    BookDetailView,
)

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("authors/", AuthorListView.as_view(), name="author-list"),
    path("", BookListView.as_view(), name="book-list"),
    path("featured/", FeaturedBookListView.as_view(), name="book-featured"),
    path("<slug:slug>/", BookDetailView.as_view(), name="book-detail"),
]