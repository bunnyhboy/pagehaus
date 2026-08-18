from django.db import models
from django.conf import settings
from books.models import Book

User = settings.AUTH_USER_MODEL


class UserLibrary(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="library"
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE
    )

    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "book"]


class BookDownload(models.Model):

    user = models.ForeignKey(
        "account.User",
        on_delete=models.CASCADE
    )

    book = models.ForeignKey(
        "books.Book",
        on_delete=models.CASCADE
    )

    downloaded_at = models.DateTimeField(auto_now_add=True)

    ip_address = models.GenericIPAddressField(null=True)

    user_agent = models.TextField(blank=True)