import django_filters
from django.db.models import Min
from app_offers.models import Offer

# FilterSet class for filtering Offer objects based on custom criteria
class OffersFilter(django_filters.FilterSet):
    # Filter offers by the ID of the user who created them
    creator_id = django_filters.NumberFilter(
        field_name='user__id',  # Filter based on related user ID
        label='creator_id',
    )

    # Filter offers by a minimum price (custom logic defined in method below)
    min_price = django_filters.NumberFilter(
        method='filter_min_price',  # Calls custom method to apply this filter
        label='min_price',
    )

    # Filter offers by a maximum delivery time (custom logic defined below)
    max_delivery_time = django_filters.NumberFilter(
        method='filter_max_delivery_time',  # Calls custom method to apply this filter
        label='max_delivery_time',
    )

    # Meta class to define which model this filter applies to and the fields allowed
    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']

    # Custom filter to find offers where the minimum price in the offer details is >= the given value
    def filter_min_price(self, queryset, name, value):
        # Annotate each offer with the minimum price found in its related details
        queryset = queryset.annotate(min_price=Min('details__price'))
        # Filter offers where the minimum price is greater than or equal to the given value
        return queryset.filter(min_price__gte=value)

    # Custom filter to find offers where the minimum delivery time in the offer details is <= the given value
    def filter_max_delivery_time(self, queryset, name, value):
        # Annotate each offer with the minimum delivery time from its related details
        queryset = queryset.annotate(min_delivery_time=Min('details__delivery_time_in_days'))
        # Filter offers where the delivery time is less than or equal to the given value
        return queryset.filter(min_delivery_time__lte=value)
