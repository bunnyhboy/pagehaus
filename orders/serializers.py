from django.db import transaction
from rest_framework import serializers

from books.models import Book
from .models import Order, OrderItem
from discount.utils import calculate_discount, record_usage


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ["id", "book", "book_title", "unit_price", "quantity", "subtotal"]
        read_only_fields = ["book_title", "unit_price", "subtotal"]


class OrderItemInputSerializer(serializers.Serializer):
    """Used only for accepting items on order creation."""

    book_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.ModelSerializer):

    items = OrderItemInputSerializer(many=True, write_only=True)
    coupon_code = serializers.CharField(required=False, allow_blank=True, write_only=True)


    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "full_name",
            "phone",
            "shipping_address",
            "city",
            "notes",
            "items",
            "subtotal",
            "total",
            "created_at",
            "coupon_code",
            "discount_total",
        ]
        read_only_fields = [
            "id", "order_number", "status", "subtotal", "total", "created_at", "discount_total",
        ]

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Order must contain at least one item.")

        book_ids = [item["book_id"] for item in items]
        books = Book.objects.filter(id__in=book_ids, is_active=True)
        books_by_id = {book.id: book for book in books}

        for item in items:
            book = books_by_id.get(item["book_id"])

            if not book:
                raise serializers.ValidationError(
                    f"Book {item['book_id']} not found or unavailable."
                )

            if book.stock < item["quantity"]:
                raise serializers.ValidationError(
                    f"'{book.title}' only has {book.stock} in stock."
                )

        return items

    @transaction.atomic
    def create(self, validated_data):

        coupon_code = validated_data.pop("coupon_code", None)
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        book_ids = [item["book_id"] for item in items_data]
        # Lock the rows so concurrent orders can't oversell the same stock.
        books = Book.objects.select_for_update().filter(id__in=book_ids)
        books_by_id = {book.id: book for book in books}



        order = Order.objects.create(user=user, **validated_data)

        subtotal = 0

        for item in items_data:
            book = books_by_id[item["book_id"]]
            quantity = item["quantity"]

            if book.stock < quantity:
                raise serializers.ValidationError(
                    f"'{book.title}' only has {book.stock} in stock."
                )

            OrderItem.objects.create(
                order=order,
                book=book,
                book_title=book.title,
                unit_price=book.price,
                quantity=quantity,
            )

            book.stock -= quantity
            book.save(update_fields=["stock"])

            subtotal += book.price * quantity

        discount_amount = 0
        coupon = None

        if coupon_code:
            from discount.models import Coupon
            try:
                coupon = Coupon.objects.get(code=coupon_code.upper().strip())
            except Coupon.DoesNotExist:
                raise serializers.ValidationError({"coupon_code": "Invalid coupon code."})

            discount_amount = calculate_discount(coupon, subtotal, user)

        order.subtotal = subtotal
        order.discount_total = discount_amount
        order.total = subtotal - discount_amount
        order.save(update_fields=["subtotal", "discount_total", "total"])

        if coupon:
            record_usage(coupon, user, order, discount_amount)

        return order


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "full_name",
            "phone",
            "shipping_address",
            "city",
            "notes",
            "items",
            "subtotal",
            "discount_total",
            "total",
            "is_cancellable",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields