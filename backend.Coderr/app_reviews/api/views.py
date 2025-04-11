from rest_framework import viewsets, filters
from ..models import Review
from .serializers import ReviewSerializer
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from app_reviews.api.filters import ReviewsFilter
from .permissions import IsCustomerUser, IsReviewer
from rest_framework.permissions import IsAuthenticated

# ViewSet for managing Review objects (create, read, update, delete)
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()  # All reviews in the database
    serializer_class = ReviewSerializer  # Serializer to use for input/output
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]  # Enable filtering and ordering
    filterset_class = ReviewsFilter  # Custom filter set for business_user_id and reviewer_id
    ordering_fields = ['updated_at', 'rating']  # Fields allowed for ordering in queries
    pagination_class = None  # No pagination applied

    # Assign permissions dynamically based on action
    def get_permissions(self):
        if self.action == 'create':
            return [IsCustomerUser()]  # Only customers can create reviews
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsReviewer()]  # Only the reviewer can modify or delete their review
        return [IsAuthenticated()]  # All other actions require authentication

    # Custom create logic to prevent duplicate reviews per business user
    def create(self, request, *args, **kwargs):
        """
        Creates a new review.
        Ensures that a user can leave only one review per business profile.
        """
        business_user_id = request.data.get("business_user")
        rating = request.data.get("rating")
        description = request.data.get("description")
        reviewer = request.user

        # Check if business user ID is provided
        if not business_user_id:
            return Response({"error": "Business user is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the reviewer has already submitted a review for this business user
        if Review.objects.filter(reviewer=reviewer, business_user_id=business_user_id).exists():
            return Response({"error": "You have already reviewed this business user."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the review
        review = Review.objects.create(
            business_user_id=business_user_id,
            reviewer=reviewer,
            rating=rating,
            description=description,
        )

        # Serialize and return the created review
        serializer = self.get_serializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)