from django.urls import path
from .views import CartView, CartItemAddView, CartItemDetailView, CartClearView

urlpatterns = [
    path("", CartView.as_view(), name="cart-detail"),
    path("items/", CartItemAddView.as_view(), name="cart-item-add"),
    path("items/<uuid:item_id>/", CartItemDetailView.as_view(), name="cart-item-detail"),
    path("clear/", CartClearView.as_view(), name="cart-clear"),
]