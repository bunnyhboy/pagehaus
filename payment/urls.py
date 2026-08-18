from django.urls import path
from .views import (
    InitiateEsewaPaymentView,
    EsewaSuccessView,
    EsewaFailureView,
    PaymentStatusView,
)

urlpatterns = [
    path("esewa/initiate/", InitiateEsewaPaymentView.as_view(), name="esewa-initiate"),
    path("esewa/success/", EsewaSuccessView.as_view(), name="esewa-success"),
    path("esewa/failure/", EsewaFailureView.as_view(), name="esewa-failure"),
    path("<uuid:order_id>/status/", PaymentStatusView.as_view(), name="payment-status"),
]