import uuid
from django.conf import settings
from django.db import models

from books.models import Book


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def subtotal(self):
        return sum((item.subtotal for item in self.items.all()), 0)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def to_order_items(self):
        """Shape cart contents to match orders.OrderItemInputSerializer."""
        return [
            {"book_id": item.book_id, "quantity": item.quantity}
            for item in self.items.all()
        ]

    def __str__(self):
        return f"Cart({self.user})"


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="cart_items")

    quantity = models.PositiveIntegerField(default=1)

    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cart", "book")
        ordering = ["-added_at"]

    @property
    def subtotal(self):
        return self.book.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.book.title}"