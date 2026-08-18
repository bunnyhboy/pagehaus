import uuid

from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from .models import Payment
from .serializers import PaymentSerializer, InitiatePaymentSerializer
from .esewa_client import EsewaClient


class InitiateEsewaPaymentView(APIView):
    """
    POST { "order_id": "..." }
    -> { "payment_url": "...", "fields": {...} }

    Frontend builds a hidden HTML form from `fields` and auto-submits it
    (POST) to `payment_url` — this is eSewa's required flow.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = Order.objects.filter(
            id=serializer.validated_data["order_id"], user=request.user
        ).first()

        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        payment = getattr(order, "payment", None)

        if payment and payment.status == Payment.Status.SUCCESS:
            return Response(
                {"detail": "This order has already been paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if payment:
            payment.transaction_uuid = uuid.uuid4()
            payment.amount = order.total
            payment.status = Payment.Status.PENDING
            payment.save(update_fields=["transaction_uuid", "amount", "status"])
        else:
            payment = Payment.objects.create(order=order, amount=order.total)

        client = EsewaClient()
        fields = client.build_form_payload(
            amount=payment.amount,
            transaction_uuid=payment.transaction_uuid,
        )

        return Response({"payment_url": client.payment_url, "fields": fields})


class EsewaSuccessView(APIView):
    """GET /payment/esewa/success/?data=<base64> — eSewa's success redirect target."""

    permission_classes = [AllowAny]

    @transaction.atomic
    def get(self, request):
        encoded = request.query_params.get("data")

        if not encoded:
            return Response({"detail": "Missing data."}, status=status.HTTP_400_BAD_REQUEST)

        client = EsewaClient()

        try:
            data = client.decode_response(encoded)
        except Exception:
            return Response({"detail": "Invalid payment response."}, status=status.HTTP_400_BAD_REQUEST)

        if not client.verify_response_signature(data):
            return Response({"detail": "Signature verification failed."}, status=status.HTTP_400_BAD_REQUEST)

        transaction_uuid = data.get("transaction_uuid")

        try:
            payment = Payment.objects.select_for_update().get(transaction_uuid=transaction_uuid)
        except Payment.DoesNotExist:
            return Response({"detail": "Payment record not found."}, status=status.HTTP_404_NOT_FOUND)

        status_response = client.check_transaction_status(
            amount=payment.amount,
            transaction_uuid=payment.transaction_uuid,
        )

        payment.raw_response = {"redirect_data": data, "status_check": status_response}

        if status_response.get("status") == "COMPLETE":
            payment.status = Payment.Status.SUCCESS
            payment.gateway_ref_id = data.get("transaction_code", "")
            payment.save(update_fields=["status", "gateway_ref_id", "raw_response"])

            order = payment.order
            if order.status == Order.Status.PENDING:
                order.status = Order.Status.PROCESSING
                order.save(update_fields=["status"])

            return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)

        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status", "raw_response"])

        return Response(
            {"detail": "Payment could not be verified.", "payment": PaymentSerializer(payment).data},
            status=status.HTTP_400_BAD_REQUEST,
        )


class EsewaFailureView(APIView):
    """GET /payment/esewa/failure/?transaction_uuid=... — eSewa's cancel/failure redirect."""

    permission_classes = [AllowAny]

    def get(self, request):
        transaction_uuid = request.query_params.get("transaction_uuid")

        if transaction_uuid:
            Payment.objects.filter(
                transaction_uuid=transaction_uuid,
                status=Payment.Status.PENDING,
            ).update(status=Payment.Status.FAILED)

        return Response({"detail": "Payment was cancelled or failed."}, status=status.HTTP_200_OK)


class PaymentStatusView(APIView):
    """GET /payment/<order_id>/status/ — for the frontend to poll if needed."""

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        payment = Payment.objects.filter(order_id=order_id, order__user=request.user).first()

        if not payment:
            return Response({"detail": "No payment found for this order."}, status=status.HTTP_404_NOT_FOUND)

        return Response(PaymentSerializer(payment).data)