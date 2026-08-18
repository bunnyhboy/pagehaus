from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["transaction_uuid", "order", "gateway", "status", "amount", "gateway_ref_id", "created_at"]
    list_filter = ["gateway", "status"]
    search_fields = ["transaction_uuid", "gateway_ref_id", "order__order_number"]
    readonly_fields = ["raw_response"]