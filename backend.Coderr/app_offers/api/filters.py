import django_filters
from django.db.models import Min
from app_offers.models import Offer

class OffersFilter(django_filters.FilterSet):
    creator_id = django_filters.NumberFilter(
        field_name='user__id',
        label='creator_id',
    )
    min_price = django_filters.NumberFilter(
        method='filter_min_price',
        label='min_price',
    )
    max_delivery_time = django_filters.NumberFilter(
        method='filter_max_delivery_time',
        label='max_delivery_time',
    )

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']

    def filter_min_price(self, queryset, name, value):
        queryset = queryset.annotate(min_price=Min('details__price'))
        return queryset.filter(min_price__gte=value)

    def filter_max_delivery_time(self, queryset, name, value):
        queryset = queryset.annotate(min_delivery_time=Min('details__delivery_time_in_days'))
        return queryset.filter(min_delivery_time__lte=value)
