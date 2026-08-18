from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ValidateCouponSerializer


class ValidateCouponView(APIView):
    """
    POST { "code": "WELCOME10", "subtotal": "1200.00" }
    -> { "code", "discount_amount", "new_total" }

    Frontend calls this at checkout preview time to show the discount
    before the order is actually submitted. Doesn't record usage.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ValidateCouponSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        coupon = serializer.validated_data["coupon"]

        return Response({
            "code": coupon.code,
            "discount_amount": serializer.validated_data["discount_amount"],
            "new_total": serializer.validated_data["new_total"],
        })