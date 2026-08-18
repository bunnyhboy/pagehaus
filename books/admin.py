from django.contrib import admin
from .models import Category, Author, Publisher, Book, BookImage


class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "price", "stock", "format", "is_active", "is_featured"]
    list_filter = ["category", "format", "language", "is_active", "is_featured"]
    search_fields = ["title", "isbn"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [BookImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Publisher)