from rest_framework import viewsets
from ..models import Order
from app_offers.models import DetailOffer
from .serializers import OrderSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from .permissions import IsCustomerUser, IsBusinessOrderOwner, IsStaff
from django.db import models
from app_user_auth.models import Profile

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(models.Q(customer_user=user) | models.Q(business_user=user))

    def get_permissions(self):
        if self.action in ['list', 'partial_update']:
            return [IsAuthenticated(), IsBusinessOrderOwner()]
        elif self.action == 'create':
            return [IsCustomerUser()]
        elif self.action in ['destroy']:
            return [IsStaff()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        offer_detail_id = request.data.get("offer_detail_id")
        
        if not offer_detail_id:
            return Response({"error": "offer_detail_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            offer_detail_id = int(offer_detail_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid request data (e.g., if 'offer_detail_id' is missing or invalid)"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            offer = DetailOffer.objects.get(id=offer_detail_id)
        except DetailOffer.DoesNotExist:
            return Response({"error": "OfferDetail not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Erstelle eine neue Order mit den Daten aus OfferDetail
        order_data = {
            "customer_user": request.user.id,
            "business_user": offer.offer.user.id,
            "title": offer.offer.title,
            "revisions": offer.revisions,
            "delivery_time_in_days": offer.delivery_time_in_days,
            "price": offer.price,
            "features": offer.features,
            "offer_type": offer.offer_type,
            "status": "in_progress",
        }

        serializer = self.get_serializer(data=order_data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        allowed_statuses = ['in_progress', 'completed', 'cancelled']
        instance = self.get_object()

        if set(request.data.keys()) != {'status'}:
            return Response(
                {"error": "Nur das Feld 'status' darf aktualisiert werden."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Gültige Statuswerte aus dem Modell
        allowed_statuses = [choice[0] for choice in Order.STATUS_CHOICE]
        new_status = request.data.get('status')

        if new_status not in allowed_statuses:
            return Response(
                {"error": f"Ungültiger Status. Erlaubt sind: {', '.join(allowed_statuses)}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Nur 'status' speichern
        instance.status = new_status
        instance.save(update_fields=['status'])

        return Response(OrderSerializer(instance).data, status=status.HTTP_200_OK)

@api_view(['GET'])
def order_count(request, business_user_id):
    if not request.user.is_authenticated:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        profile = Profile.objects.get(pk=business_user_id)
        if profile.type != 'business':
            return Response({"error": "User is not a business user"}, status=status.HTTP_400_BAD_REQUEST)
    except Profile.DoesNotExist:
        return Response({"error": "Business user not found"}, status=status.HTTP_404_NOT_FOUND)

    order_count = Order.objects.filter(business_user_id=business_user_id, status='in_progress').count()
    return Response({"order_count": order_count}, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def completed_order_count(request, business_user_id):
    if not request.user.is_authenticated:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        profile = Profile.objects.get(pk=business_user_id)
        if profile.type != 'business':
            return Response({"error": "User is not a business user"}, status=status.HTTP_400_BAD_REQUEST)
    except Profile.DoesNotExist:
        return Response({"error": "Business user not found"}, status=status.HTTP_404_NOT_FOUND)

    order_count = Order.objects.filter(business_user_id=business_user_id, status='completed').count()
    return Response({"order_count": order_count}, status=status.HTTP_200_OK)