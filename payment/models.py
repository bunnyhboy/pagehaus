import uuid
from django.db import models

from orders.models import Order


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    class Gateway(models.TextChoices):
        ESEWA = "esewa", "eSewa"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")

    # Regenerated on each retry attempt — eSewa treats each transaction_uuid
    # as a distinct transaction for status-check purposes.
    transaction_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    gateway = models.CharField(max_length=20, choices=Gateway.choices, default=Gateway.ESEWA)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gateway_ref_id = models.CharField(max_length=100, blank=True)

    raw_response = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment({self.transaction_uuid}) - {self.status}"