from rest_framework import viewsets, generics
from ..models import Offer, DetailOffer
from .serializers import OfferListSerializer, OfferCreateSerializer, OfferDetailSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny


class OfferView(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == ['list', 'retrieve']: 
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
    permission_classes = [IsAuthenticated]