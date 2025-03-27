from rest_framework import viewsets, generics, filters
from ..models import Offer, DetailOffer
from .serializers import OfferListSerializer, OfferCreateSerializer, OfferDetailSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from app_offers.api.filters import OffersFilter
from .permissions import IsBusinessUser, IsOwner
from rest_framework.pagination import PageNumberPagination

class OfferPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 6

class OfferView(viewsets.ModelViewSet):
    queryset = Offer.objects.all().order_by('-updated_at')
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = OffersFilter
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']
    pagination_class = OfferPagination

    def get_permissions(self):
        if self.action == 'create':
            return [IsBusinessUser()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwner()]
        return [IsAuthenticatedOrReadOnly()]
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']: 
            return OfferListSerializer
        elif self.action in ['create', 'update', 'partial_update']: 
            return OfferCreateSerializer
        return OfferListSerializer  
    
    def perform_create(self, serializer):
        """ Setzt den aktuellen Benutzer als Eigentümer des Angebots """
        serializer.save(user=self.request.user)


class OfferDetailView(generics.RetrieveAPIView):
    queryset = DetailOffer.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]