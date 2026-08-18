from rest_framework import serializers


class OverviewSerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_books = serializers.IntegerField()
    low_stock_count = serializers.IntegerField()
    active_coupons = serializers.IntegerField()


class SalesTrendPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    order_count = serializers.IntegerField()


class TopBookSerializer(serializers.Serializer):
    book_id = serializers.UUIDField()
    title = serializers.CharField()
    units_sold = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)


class LowStockBookSerializer(serializers.Serializer):
    book_id = serializers.UUIDField()
    title = serializers.CharField()
    stock = serializers.IntegerField()


class OrderStatusBreakdownSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()