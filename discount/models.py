import uuid
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class Coupon(models.Model):

    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage"
        FIXED = "fixed", "Fixed Amount"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    code = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=255, blank=True)

    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2)

    # Only meaningful for percentage coupons — caps the peso/rupee amount off.
    max_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    usage_limit = models.PositiveIntegerField(
        blank=True, null=True, help_text="Total times this code can be used, across all users."
    )
    per_user_limit = models.PositiveIntegerField(default=1)

    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.code = self.code.upper().strip()
        super().save(*args, **kwargs)

    @property
    def total_uses(self):
        return self.usages.count()

    @property
    def is_expired(self):
        if self.valid_until:
            return timezone.now() > self.valid_until
        return False

    @property
    def is_upcoming(self):
        return timezone.now() < self.valid_from

    def __str__(self):
        return self.code


class CouponUsage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="usages")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coupon_usages"
    )
    order = models.OneToOneField(
        "orders.Order", on_delete=models.CASCADE, related_name="coupon_usage"
    )

    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)

    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.coupon.code} used by {self.user}"