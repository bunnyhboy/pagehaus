from rest_framework import serializers

from books.models import Book
from books.serializers import BookListSerializer
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "book", "quantity", "subtotal", "added_at"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "subtotal", "total_items", "updated_at"]


class AddCartItemSerializer(serializers.Serializer):
    book_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, data):
        try:
            book = Book.objects.get(id=data["book_id"], is_active=True)
        except Book.DoesNotExist:
            raise serializers.ValidationError({"book_id": "Book not found or unavailable."})

        cart = self.context["cart"]
        existing_item = cart.items.filter(book=book).first()
        already_in_cart = existing_item.quantity if existing_item else 0
        requested_total = already_in_cart + data["quantity"]

        if book.stock < requested_total:
            raise serializers.ValidationError(
                f"Only {book.stock} of '{book.title}' available "
                f"({already_in_cart} already in your cart)."
            )

        data["book"] = book
        return data


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)

    def validate_quantity(self, value):
        item = self.context["item"]
        if item.book.stock < value:
            raise serializers.ValidationError(
                f"Only {item.book.stock} of '{item.book.title}' available."
            )
        return value