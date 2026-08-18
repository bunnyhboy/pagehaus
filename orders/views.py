from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer


class OrderListCreateView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderSerializer


class OrderDetailView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderCancelView(APIView):

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, id):
        try:
            order = Order.objects.select_for_update().get(id=id, user=request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if not order.is_cancellable:
            return Response(
                {"detail": f"Order in '{order.status}' status cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Restock items
        for item in order.items.select_related("book"):
            if item.book:
                item.book.stock += item.quantity
                item.book.save(update_fields=["stock"])

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)