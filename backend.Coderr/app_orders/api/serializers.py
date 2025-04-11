from rest_framework import serializers
from ..models import Order
from app_user_auth.models import Profile

# Serializer for handling Order creation, update, and retrieval
class OrderSerializer(serializers.ModelSerializer):
    # customer_user must be a Profile with type 'customer'
    customer_user = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.filter(type='customer')
    )

    # business_user must be a Profile with type 'business'
    business_user = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.filter(type='business')
    )

    class Meta:
        model = Order  # Specifies the model this serializer is based on
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at'
        ]

        # Fields that should not be editable via the API
        read_only_fields = ['id', 'customer_user', 'business_user', 'created_at']