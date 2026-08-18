from django.db.models import Avg, Count
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import Book
from .models import Review
from .serializers import (
    ReviewSerializer,
    ReviewCreateSerializer,
    ReviewUpdateSerializer,
    BookReviewSummarySerializer,
)


class BookReviewListCreateView(generics.ListCreateAPIView):
    """
    GET  /books/<book_id>/reviews/        -> approved reviews for a book
    POST /books/<book_id>/reviews/        -> create a review for a book
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(
            book_id=self.kwargs["book_id"], is_approved=True
        ).select_related("user")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["book"] = kwargs["book_id"]

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()

        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class MyReviewDetailView(APIView):
    """
    Manage the requesting user's own review on a given book.
    GET/PATCH/DELETE /books/<book_id>/reviews/me/
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, request, book_id):
        return Review.objects.filter(book_id=book_id, user=request.user).first()

    def get(self, request, book_id):
        review = self.get_object(request, book_id)
        if not review:
            return Response({"detail": "You haven't reviewed this book."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ReviewSerializer(review).data)

    def patch(self, request, book_id):
        review = self.get_object(request, book_id)
        if not review:
            return Response({"detail": "You haven't reviewed this book."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewUpdateSerializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(ReviewSerializer(review).data)

    def delete(self, request, book_id):
        review = self.get_object(request, book_id)
        if not review:
            return Response({"detail": "You haven't reviewed this book."}, status=status.HTTP_404_NOT_FOUND)

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookReviewSummaryView(APIView):
    """GET /books/<book_id>/reviews/summary/ -> average + count + breakdown."""

    def get(self, request, book_id):
        book = Book.objects.filter(id=book_id).first()
        if not book:
            return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

        reviews = Review.objects.filter(book=book, is_approved=True)

        aggregate = reviews.aggregate(average_rating=Avg("rating"), review_count=Count("id"))

        breakdown = {str(i): 0 for i in range(1, 6)}
        counts = reviews.values("rating").annotate(count=Count("id"))
        for row in counts:
            breakdown[str(row["rating"])] = row["count"]

        data = {
            "average_rating": round(aggregate["average_rating"] or 0, 2),
            "review_count": aggregate["review_count"],
            "rating_breakdown": breakdown,
        }

        return Response(BookReviewSummarySerializer(data).data)