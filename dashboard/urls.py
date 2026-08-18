from django.urls import path
from .views import (
    OverviewView,
    SalesTrendView,
    TopBooksView,
    LowStockView,
    OrderStatusBreakdownView,
)

urlpatterns = [
    path("overview/", OverviewView.as_view(), name="dashboard-overview"),
    path("sales-trend/", SalesTrendView.as_view(), name="dashboard-sales-trend"),
    path("top-books/", TopBooksView.as_view(), name="dashboard-top-books"),
    path("low-stock/", LowStockView.as_view(), name="dashboard-low-stock"),
    path("order-status/", OrderStatusBreakdownView.as_view(), name="dashboard-order-status"),
]