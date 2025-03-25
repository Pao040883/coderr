from django.db.models import Avg
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from app_user_auth.models import Profile
from app_offers.models import Offer
from app_reviews.models import Review


class BaseInfoView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(self._get_statistics(), status=status.HTTP_200_OK)

    def _get_statistics(self):
        avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0.0
        return {
            'review_count': Review.objects.count(),
            'average_rating': round(avg_rating, 1),
            'business_profile_count': Profile.objects.filter(type='business').count(),
            'offer_count': Offer.objects.count(),
        }