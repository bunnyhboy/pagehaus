from django.urls import path
from .views import OrderListCreateView, OrderDetailView, OrderCancelView

urlpatterns = [
    path("", OrderListCreateView.as_view(), name="order-list-create"),
    path("<uuid:id>/", OrderDetailView.as_view(), name="order-detail"),
    path("<uuid:id>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
]