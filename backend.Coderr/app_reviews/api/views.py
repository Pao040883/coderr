from rest_framework import viewsets, filters
from ..models import Review
from .serializers import ReviewSerializer
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from app_reviews.api.filters import ReviewsFilter
from .permissions import IsCustomerUser, IsReviewer
from rest_framework.permissions import IsAuthenticated

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewsFilter
    ordering_fields = ['updated_at', 'rating']
    pagination_class = None

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsCustomerUser()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsReviewer()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """
        Erstellt eine neue Bewertung. Stellt sicher, dass der Benutzer nur eine Bewertung pro Geschäftsprofil abgeben kann.
        """
        business_user_id = request.data.get("business_user")
        rating = request.data.get("rating")
        description = request.data.get("description")
        reviewer = request.user

        # Prüfen, ob der Geschäftsbenutzer angegeben wurde
        if not business_user_id:
            return Response({"error": "Business user is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Prüfen, ob der Benutzer bereits eine Bewertung für diesen Geschäftsbenutzer abgegeben hat
        if Review.objects.filter(reviewer=reviewer, business_user_id=business_user_id).exists():
            return Response({"error": "You have already reviewed this business user."}, status=status.HTTP_403_FORBIDDEN)

        # Bewertung erstellen
        review = Review.objects.create(
            business_user_id=business_user_id,
            reviewer=reviewer,
            rating=rating,
            description=description,
        )

        serializer = self.get_serializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)