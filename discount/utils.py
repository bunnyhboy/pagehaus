from django.utils import timezone
from rest_framework import serializers
from decimal import Decimal

from .models import Coupon


def calculate_discount(coupon: Coupon, subtotal, user) -> "Decimal":
    """
    Validates a coupon against the given subtotal/user and returns the
    discount amount. Raises serializers.ValidationError if not applicable.
    Does NOT record usage — call record_usage() after the order is created.
    """

    if not coupon.is_active:
        raise serializers.ValidationError("This coupon is no longer active.")

    now = timezone.now()

    if now < coupon.valid_from:
        raise serializers.ValidationError("This coupon is not active yet.")

    if coupon.is_expired:
        raise serializers.ValidationError("This coupon has expired.")

    if subtotal < coupon.min_order_amount:
        raise serializers.ValidationError(
            f"This coupon requires a minimum order of {coupon.min_order_amount}."
        )

    if coupon.usage_limit is not None and coupon.total_uses >= coupon.usage_limit:
        raise serializers.ValidationError("This coupon has reached its usage limit.")

    user_uses = coupon.usages.filter(user=user).count()
    if user_uses >= coupon.per_user_limit:
        raise serializers.ValidationError("You've already used this coupon.")

    if coupon.discount_type == Coupon.DiscountType.PERCENTAGE:
        discount = subtotal * (coupon.value / 100)
        if coupon.max_discount_amount is not None:
            discount = min(discount, coupon.max_discount_amount)
    else:
        discount = coupon.value

    # Never discount more than the subtotal itself.
    discount = min(discount, subtotal)

    return discount


def record_usage(coupon: Coupon, user, order, discount_amount):
    from .models import CouponUsage

    return CouponUsage.objects.create(
        coupon=coupon,
        user=user,
        order=order,
        discount_amount=discount_amount,
    )