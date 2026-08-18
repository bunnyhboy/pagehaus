def has_verified_purchase(user, book):
    """
    True if the user has a delivered order containing this book.
    Import kept local to avoid any import-order issues between apps.
    """
    from orders.models import Order, OrderItem

    return OrderItem.objects.filter(
        order__user=user,
        order__status=Order.Status.DELIVERED,
        book=book,
    ).exists()