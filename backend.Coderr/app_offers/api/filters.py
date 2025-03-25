import django_filters
from app_offers.models import Offer

class OffersFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='min_price', lookup_expr='gte')
    min_delivery_time = django_filters.NumberFilter(field_name='min_delivery_time', lookup_expr='lte')
    creator_id = django_filters.NumberFilter(field_name='user__id')

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'min_delivery_time']