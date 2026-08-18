from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import CartSerializer, AddCartItemSerializer, UpdateCartItemSerializer


class CartView(APIView):
    """GET the current user's cart (auto-created if it doesn't exist yet)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)


class CartItemAddView(APIView):
    """POST { "book_id": "...", "quantity": 1 } -> adds or increments."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)

        serializer = AddCartItemSerializer(data=request.data, context={"cart": cart})
        serializer.is_valid(raise_exception=True)

        book = serializer.validated_data["book"]
        quantity = serializer.validated_data["quantity"]

        item, created = CartItem.objects.get_or_create(
            cart=cart, book=book, defaults={"quantity": quantity}
        )

        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    """PATCH { "quantity": n } to update, DELETE to remove a single item."""

    permission_classes = [IsAuthenticated]

    def get_item(self, request, item_id):
        return CartItem.objects.filter(id=item_id, cart__user=request.user).select_related("book").first()

    def patch(self, request, item_id):
        item = self.get_item(request, item_id)
        if not item:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateCartItemSerializer(data=request.data, context={"item": item})
        serializer.is_valid(raise_exception=True)

        item.quantity = serializer.validated_data["quantity"]
        item.save(update_fields=["quantity"])

        return Response(CartSerializer(item.cart).data)

    def delete(self, request, item_id):
        item = self.get_item(request, item_id)
        if not item:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        cart = item.cart
        item.delete()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class CartClearView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)