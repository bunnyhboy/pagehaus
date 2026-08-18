from rest_framework import serializers

from .models import Coupon
from .utils import calculate_discount


class CouponSerializer(serializers.ModelSerializer):

    class Meta:
        model = Coupon
        fields = [
            "id", "code", "description", "discount_type", "value",
            "max_discount_amount", "min_order_amount",
            "valid_from", "valid_until", "is_active",
        ]


class ValidateCouponSerializer(serializers.Serializer):

    code = serializers.CharField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)

    def validate(self, data):
        try:
            coupon = Coupon.objects.get(code=data["code"].upper().strip())
        except Coupon.DoesNotExist:
            raise serializers.ValidationError({"code": "Invalid coupon code."})

        user = self.context["request"].user
        discount_amount = calculate_discount(coupon, data["subtotal"], user)

        data["coupon"] = coupon
        data["discount_amount"] = discount_amount
        data["new_total"] = data["subtotal"] - discount_amount

        return data