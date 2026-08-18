from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = [
            "id", "order", "transaction_uuid", "gateway",
            "status", "amount", "gateway_ref_id", "created_at", "updated_at",
        ]
        read_only_fields = fields


class InitiatePaymentSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()