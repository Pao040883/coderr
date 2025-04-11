from django.db.models import Avg
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from app_user_auth.models import Profile
from app_offers.models import Offer
from app_reviews.models import Review


# API view that provides general statistical information
class BaseInfoView(APIView):
    # Disable authentication and permission checks for this view
    authentication_classes = []
    permission_classes = []

    # Handle GET requests to this endpoint
    def get(self, request):
        return Response(self._get_statistics(), status=status.HTTP_200_OK)

    # Private method to calculate and return statistical data
    def _get_statistics(self):
        # Calculate the average rating across all reviews
        # If there are no reviews, default to 0.0
        avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0.0

        # Return a dictionary with the calculated statistics
        return {
            'review_count': Review.objects.count(),  # Total number of reviews
            'average_rating': round(avg_rating, 1),  # Average rating rounded to one decimal place
            'business_profile_count': Profile.objects.filter(type='business').count(),  # Count of business profiles
            'offer_count': Offer.objects.count(),  # Total number of offers
        }
