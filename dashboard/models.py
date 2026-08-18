from django.db import models
from django.conf import settings


class AnalyticsEvent(models.Model):

    EVENT_TYPES = [
        ("book_view", "Book View"),
        ("book_download", "Book Download"),
        ("purchase", "Purchase"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="analytics_events"
    )

    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES,
        db_index=True
    )

    book = models.ForeignKey(
        "books.Book",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_events"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    def __str__(self):
        return f"{self.event_type} - {self.created_at}"