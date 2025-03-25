import django_filters
from app_reviews.models import Review

class ReviewsFilter(django_filters.FilterSet):
    # business_user_id = django_filters.NumberFilter(field_name='business_user')
    # reviewer_id = django_filters.NumberFilter(field_name='reviewer')

    class Meta:
        model = Review
        fields = ['business_user_id', 'reviewer']