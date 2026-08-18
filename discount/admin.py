from django.contrib import admin
from .models import Coupon, CouponUsage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        "code", "discount_type", "value", "min_order_amount",
        "usage_limit", "is_active", "valid_from", "valid_until",
    ]
    list_filter = ["discount_type", "is_active"]
    search_fields=["code"]


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ["coupon", "user", "order", "discount_amount", "used_at"]
    readonly_fields = ["coupon", "user", "order", "discount_amount", "used_at"]