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
        elif self.action == 'retrieve':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwner()]
        return [AllowAny()]
    
    def get_serializer_class(self):
        if self.action in ['list']: 
            return OfferListSerializer
        elif self.action in ['retrieve']: 
            return OfferSingleSerializer
        elif self.action in ['create', 'update', 'partial_update']: 
            return OfferCreateSerializer
        return OfferListSerializer  
    
    def perform_create(self, serializer):
        """ Setzt den aktuellen Benutzer als Eigentümer des Angebots """
        serializer.save(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
            offer = get_object_or_404(Offer, pk=kwargs.get('pk'))

            if offer.user != request.user:
                raise PermissionDenied("Authentifizierter Benutzer ist nicht der Eigentümer des Angebots.")

            serializer = self.get_serializer(offer, data=request.data, partial=True)
            if serializer.is_valid():
                self.perform_update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OfferDetailView(generics.RetrieveAPIView):
    queryset = DetailOffer.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]