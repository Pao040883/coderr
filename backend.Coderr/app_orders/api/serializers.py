from rest_framework import serializers
from ..models import Order
from app_user_auth.models import Profile

class OrderSerializer(serializers.ModelSerializer):
    customer_user = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.filter(type='customer')
    )
    business_user = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.filter(type='business')
    )

    class Meta:
        model = Order
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

        read_only_fields = ['id', 'customer_user', 'business_user', 'created_at']  