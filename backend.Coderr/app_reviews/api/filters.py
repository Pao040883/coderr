import django_filters
from app_reviews.models import Review

class ReviewsFilter(django_filters.FilterSet):
    class Meta:
        model = Review
        fields = ['business_user_id', 'reviewer_id']