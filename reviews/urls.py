from django.urls import path
from .views import BookReviewListCreateView, MyReviewDetailView, BookReviewSummaryView

urlpatterns = [
    path("<uuid:book_id>/reviews/", BookReviewListCreateView.as_view(), name="book-review-list-create"),
    path("<uuid:book_id>/reviews/me/", MyReviewDetailView.as_view(), name="book-review-mine"),
    path("<uuid:book_id>/reviews/summary/", BookReviewSummaryView.as_view(), name="book-review-summary"),
]