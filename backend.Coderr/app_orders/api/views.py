from rest_framework import viewsets
from ..models import Order
from app_offers.models import DetailOffer
from .serializers import OrderSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from .permissions import IsCustomerUser, IsBusinessUser, IsBusinessOrderOwner, IsStaff
from django.db import models

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(models.Q(customer_user=user) | models.Q(business_user=user))

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated(), IsBusinessOrderOwner()]
        elif self.action == 'create':
            return [IsAuthenticated(), IsCustomerUser()]
        elif self.action in ['partial_update']:
            return [IsAuthenticated(), IsBusinessUser()]
        elif self.action in ['destroy']:
            return [IsAuthenticated(), IsStaff()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        offer_detail_id = request.data.get("offer_detail_id")
        
        if not offer_detail_id:
            return Response({"error": "offer_detail_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            offer = DetailOffer.objects.get(id=offer_detail_id)
        except DetailOffer.DoesNotExist:
            return Response({"error": "OfferDetail not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Erstelle eine neue Order mit den Daten aus OfferDetail
        order_data = {
            "customer_user": request.user.id,
            "business_user": offer.offer.user.id,
            "title": offer.title,
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
        instance = self.get_object()
        if 'status' not in request.data:
            return Response({"error": "Only 'status' can be updated"}, status=status.HTTP_400_BAD_REQUEST)
        
        instance.status = request.data['status']
        instance.save()
        return Response(OrderSerializer(instance).data, status=status.HTTP_200_OK)

@api_view(['GET'])
def order_count(request, business_user_id):
    if not request.user.is_authenticated:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        order_count = Order.objects.filter(business_user_id=business_user_id, status='in_progress').count()
        return Response({"order_count": order_count}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Internal Server Error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def completed_order_count(request, business_user_id):
    if not request.user.is_authenticated:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        completed_order_count = Order.objects.filter(business_user_id=business_user_id, status='completed').count()
        return Response({"completed_order_count": completed_order_count}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Internal Server Error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)