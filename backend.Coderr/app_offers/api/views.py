from rest_framework import viewsets, generics, filters, status
from rest_framework.response import Response
from ..models import Offer, DetailOffer
from .serializers import OfferListSerializer, OfferCreateSerializer, OfferDetailSerializer, OfferSingleSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from app_offers.api.filters import OffersFilter
from .permissions import IsBusinessUser, IsOwner
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

# Custom pagination class with default page size of 6
class OfferPagination(PageNumberPagination):
    page_size_query_param = 'page_size'  # Allows overriding the page size via query param
    page_size = 6


# Main ViewSet to handle CRUD operations for Offer objects
class OfferView(viewsets.ModelViewSet):
    queryset = Offer.objects.all().order_by('-updated_at')  # Order offers by last update time
    filter_backends = [
        DjangoFilterBackend,         # Allows filtering using django-filters
        filters.OrderingFilter,      # Allows ordering results via query param
        filters.SearchFilter         # Enables search across specified fields
    ]
    filterset_class = OffersFilter  # Custom filterset with business-specific filters
    ordering_fields = ['updated_at', 'min_price']  # Fields that can be used for ordering
    search_fields = ['title', 'description']       # Fields that can be searched via full text
    pagination_class = OfferPagination             # Use custom pagination settings

    # Assign permissions dynamically based on action (e.g. create, update)
    def get_permissions(self):
        if self.action == 'create':
            return [IsBusinessUser()]  # Only business users can create offers
        elif self.action == 'retrieve':
            return [IsAuthenticated()]  # Viewing details requires login
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwner()]  # Editing/deleting requires ownership
        return [AllowAny()]  # All other actions (e.g., list) are public

    # Assign serializer class dynamically based on action
    def get_serializer_class(self):
        if self.action == 'list': 
            return OfferListSerializer  # Used for listing all offers
        elif self.action == 'retrieve': 
            return OfferSingleSerializer  # Used for showing one detailed offer
        elif self.action in ['create', 'update', 'partial_update']: 
            return OfferCreateSerializer  # Used for creating and updating offers
        return OfferListSerializer  # Fallback to list serializer

    # Called when a new offer is created
    def perform_create(self, serializer):
        """Sets the current authenticated user as the offer owner"""
        serializer.save(user=self.request.user)

    # Custom implementation for partial updates with permission check
    def partial_update(self, request, *args, **kwargs):
        # Get the offer object or return 404
        offer = get_object_or_404(Offer, pk=kwargs.get('pk'))

        # Ensure that the requesting user is the owner
        if offer.user != request.user:
            raise PermissionDenied("Authenticated user is not the owner of this offer.")

        # Validate and save the update
        serializer = self.get_serializer(offer, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View to retrieve a single DetailOffer instance (requires authentication)
class OfferDetailView(generics.RetrieveAPIView):
    queryset = DetailOffer.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]