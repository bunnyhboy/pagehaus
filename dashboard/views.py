from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import Book
from orders.models import Order, OrderItem
from discount.models import Coupon

from .serializers import (
    OverviewSerializer,
    SalesTrendPointSerializer,
    TopBookSerializer,
    LowStockBookSerializer,
    OrderStatusBreakdownSerializer,
)

User = get_user_model()

LOW_STOCK_THRESHOLD = 5

# Orders in these statuses count toward revenue; cancelled orders don't.
REVENUE_STATUSES = [
    Order.Status.PROCESSING,
    Order.Status.SHIPPED,
    Order.Status.DELIVERED,
]


class OverviewView(APIView):
    """
    High-level snapshot for the dashboard landing page.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        revenue_orders = Order.objects.filter(status__in=REVENUE_STATUSES)

        data = {
            "total_revenue": revenue_orders.aggregate(s=Sum("total"))["s"] or 0,
            "total_orders": Order.objects.count(),
            "pending_orders": Order.objects.filter(status=Order.Status.PENDING).count(),
            "total_customers": User.objects.count(),
            "total_books": Book.objects.filter(is_active=True).count(),
            "low_stock_count": Book.objects.filter(
                is_active=True, stock__lte=LOW_STOCK_THRESHOLD
            ).count(),
            "active_coupons": Coupon.objects.filter(is_active=True).count(),
        }

        return Response(OverviewSerializer(data).data)


class SalesTrendView(APIView):
    """
    Daily revenue for the last N days.
    ?days=7|30|90 (default 30)
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            days = int(request.query_params.get("days", 30))
        except ValueError:
            days = 30
        days = max(1, min(days, 365))

        since = timezone.now() - timedelta(days=days)

        queryset = (
            Order.objects.filter(status__in=REVENUE_STATUSES, created_at__gte=since)
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(revenue=Sum("total"), order_count=Count("id"))
            .order_by("date")
        )

        return Response(SalesTrendPointSerializer(queryset, many=True).data)


class TopBooksView(APIView):
    """
    Best-selling books by quantity, based on non-cancelled orders.
    ?limit=10 (default), ?days=<n> to restrict to a recent window.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 10))
        except ValueError:
            limit = 10
        limit = max(1, min(limit, 50))

        queryset = OrderItem.objects.filter(
            order__status__in=REVENUE_STATUSES
        )

        days = request.query_params.get("days")
        if days:
            try:
                since = timezone.now() - timedelta(days=int(days))
                queryset = queryset.filter(order__created_at__gte=since)
            except ValueError:
                pass

        queryset = (
            queryset.values("book_id", "book_title")
            .annotate(
                units_sold=Sum("quantity"),
                revenue=Sum(F("unit_price") * F("quantity")),
            )
            .order_by("-units_sold")[:limit]
        )

        data = [
            {
                "book_id": row["book_id"],
                "title": row["book_title"],
                "units_sold": row["units_sold"],
                "revenue": row["revenue"] or 0,
            }
            for row in queryset
        ]

        return Response(TopBookSerializer(data, many=True).data)


class LowStockView(APIView):
    """Active books at or below the low-stock threshold, lowest first."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            threshold = int(request.query_params.get("threshold", LOW_STOCK_THRESHOLD))
        except ValueError:
            threshold = LOW_STOCK_THRESHOLD

        books = Book.objects.filter(
            is_active=True, stock__lte=threshold
        ).order_by("stock").values("id", "title", "stock")

        data = [
            {"book_id": b["id"], "title": b["title"], "stock": b["stock"]}
            for b in books
        ]

        return Response(LowStockBookSerializer(data, many=True).data)


class OrderStatusBreakdownView(APIView):
    """Count of orders grouped by status — feeds a pie/bar chart."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = (
            Order.objects.values("status")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return Response(OrderStatusBreakdownSerializer(queryset, many=True).data)