from rest_framework import serializers

from .models import Review
from .utils import has_verified_purchase


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id", "book", "username", "rating", "title", "comment",
            "is_verified_purchase", "created_at", "updated_at",
        ]
        read_only_fields = ["is_verified_purchase", "created_at", "updated_at"]


class ReviewCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ["id", "book", "rating", "title", "comment"]

    def validate(self, data):
        request = self.context["request"]
        user = request.user
        book = data["book"]

        if Review.objects.filter(book=book, user=user).exists():
            raise serializers.ValidationError(
                "You've already reviewed this book. Edit your existing review instead."
            )

        from django.conf import settings
        require_purchase = getattr(settings, "REVIEWS_REQUIRE_VERIFIED_PURCHASE", True)

        if require_purchase and not has_verified_purchase(user, book):
            raise serializers.ValidationError(
                "You can only review books you've purchased and received."
            )

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["is_verified_purchase"] = has_verified_purchase(
            user, validated_data["book"]
        )
        return Review.objects.create(user=user, **validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ["rating", "title", "comment"]


class BookReviewSummarySerializer(serializers.Serializer):
    average_rating = serializers.FloatField()
    review_count = serializers.IntegerField()
    rating_breakdown = serializers.DictField(child=serializers.IntegerField())