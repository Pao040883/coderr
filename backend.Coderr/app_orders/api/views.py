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

# ViewSet for managing Order objects
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    # Return only orders related to the current user (as customer or business)
    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(models.Q(customer_user=user) | models.Q(business_user=user))

    # Assign permissions based on the action
    def get_permissions(self):
        if self.action in ['list', 'partial_update']:
            return [IsAuthenticated(), IsBusinessOrderOwner()]  # Only the business user who owns the order
        elif self.action == 'create':
            return [IsCustomerUser()]  # Only customer users can create orders
        elif self.action in ['destroy']:
            return [IsStaff()]  # Only staff users can delete orders
        return [IsAuthenticated()]  # Default to requiring authentication


    # Custom order creation using a detail offer reference
    def create(self, request, *args, **kwargs):
        from .utils import prepare_order_data

        order_data_or_response = prepare_order_data(request)
        if isinstance(order_data_or_response, Response):
            return order_data_or_response

        serializer = self.get_serializer(data=order_data_or_response)
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # Allow only partial updates to the order status
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Ensure only the 'status' field is being updated
        if set(request.data.keys()) != {'status'}:
            return Response(
                {"error": "Only the 'status' field may be updated."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate the new status value against allowed choices
        allowed_statuses = [choice[0] for choice in Order.STATUS_CHOICE]
        new_status = request.data.get('status')

        if new_status not in allowed_statuses:
            return Response(
                {"error": f"Invalid status. Allowed values: {', '.join(allowed_statuses)}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the status field only
        instance.status = new_status
        instance.save(update_fields=['status'])

        return Response(OrderSerializer(instance).data, status=status.HTTP_200_OK)


# API endpoint to get the number of in-progress orders for a given business user
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

    # Count orders with status 'in_progress' for the business user
    order_count = Order.objects.filter(business_user_id=business_user_id, status='in_progress').count()
    return Response({"order_count": order_count}, status=status.HTTP_200_OK)


# API endpoint to get the number of completed orders for a given business user
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

    # Count orders with status 'completed' for the business user
    order_count = Order.objects.filter(business_user_id=business_user_id, status='completed').count()
    return Response({"completed_order_count": order_count}, status=status.HTTP_200_OK)