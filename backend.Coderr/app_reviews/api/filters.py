import django_filters
from app_reviews.models import Review

# FilterSet for filtering Review objects based on provided fields
class ReviewsFilter(django_filters.FilterSet):
    class Meta:
        model = Review  # The model to filter
        fields = [
            'business_user_id',  # Allows filtering reviews by the reviewed business user
            'reviewer_id'        # Allows filtering reviews by the user who wrote the review
        ]