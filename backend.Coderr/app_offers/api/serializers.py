from rest_framework import serializers
from ..models import Offer, DetailOffer
from django.db.models import Min
from rest_framework.reverse import reverse


# Mixin to provide user-related fields in serialized output
class UserMixin(serializers.Serializer):
    user_details = serializers.SerializerMethodField()

    def get_user_details(self, obj):
        # Returns basic information about the user associated with the offer
        return {
            "first_name": obj.user.first_name if obj.user else "",
            "last_name": obj.user.last_name if obj.user else "",
            "username": obj.user.username if obj.user else "",
        }


# Serializer for listing multiple offers with summarized data
class OfferListSerializer(UserMixin, serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 
            'created_at', 'updated_at', 'details', 'min_price', 
            'min_delivery_time', 'user_details'
        ]

    def get_details(self, obj):
        # Returns a list of URLs pointing to the related offer details
        return [
            {"id": detail.id, "url": f"/offerdetails/{detail.id}/"}
            for detail in obj.details.all()
        ]

    def get_min_price(self, obj):
        # Returns the lowest price among all related detail offers
        return obj.details.aggregate(Min("price"))["price__min"]

    def get_min_delivery_time(self, obj):
        # Returns the shortest delivery time among all related detail offers
        return obj.details.aggregate(Min("delivery_time_in_days"))["delivery_time_in_days__min"]

    def validate_details(self, value):
        # Validates that exactly 3 details are provided
        if len(value) != 3:
            raise serializers.ValidationError({"detail": ["3 details required"]})

        # Validates that one of each offer type is present: basic, standard, premium
        offer_types = {detail['offer_type'] for detail in value}
        required_type = {'basic', 'standard', 'premium'}

        if offer_types != required_type:
            raise serializers.ValidationError({"detail": ["1 Basic, 1 Standard, and 1 Premium detail required"]})

        return value


# Serializer for a single offer (used for detail views)
class OfferSingleSerializer(UserMixin, serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 
            'created_at', 'updated_at', 'details', 'min_price', 
            'min_delivery_time', 'user_details'
        ]

    def get_details(self, obj):
        # Returns a list of absolute URLs for each detail using request context
        request = self.context.get('request')
        return [
            {"id": detail.id, "url": request.build_absolute_uri(f"/api/offerdetails/{detail.id}/") if request else f"/api/offerdetails/{detail.id}/"}
            for detail in obj.details.all()
        ]

    def get_min_price(self, obj):
        return obj.details.aggregate(Min("price"))["price__min"]

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(Min("delivery_time_in_days"))["delivery_time_in_days__min"]

    def validate_details(self, value):
        if len(value) != 3:
            raise serializers.ValidationError({"detail": ["3 details required"]})

        offer_types = {detail['offer_type'] for detail in value}
        required_type = {'basic', 'standard', 'premium'}

        if offer_types != required_type:
            raise serializers.ValidationError({"detail": ["1 Basic, 1 Standard, and 1 Premium detail required"]})

        return value


# Serializer for a single detail of an offer
class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailOffer
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days', 
            'price', 'features', 'offer_type'
        ]


# Serializer used when creating or updating an offer with nested details
class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'image', 'description', 
            'created_at', 'updated_at', 'details'
        ]

    def validate_details(self, value):
        """Validates the details only during creation of a new offer"""
        if self.instance is None:  # Only validate on create, not on update
            if len(value) != 3:
                raise serializers.ValidationError({"detail": ["3 details required"]})

            offer_types = {detail['offer_type'] for detail in value}
            required_types = {'basic', 'standard', 'premium'}

            if offer_types != required_types:
                raise serializers.ValidationError({"detail": ["1 Basic, 1 Standard, and 1 Premium detail required"]})

        return value

    def create(self, validated_data):
        """Creates a new offer and its associated detail entries"""
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            DetailOffer.objects.create(offer=offer, **detail_data)

        return offer

    def update(self, instance, validated_data):
        """Updates an existing offer and its detail entries"""
        details_data = validated_data.pop('details', None)

        # Update the fields of the offer instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # If detail data is provided, update or create related details
        if details_data is not None:
            existing_details = {detail.offer_type: detail for detail in instance.details.all()}

            for detail_data in details_data:
                offer_type = detail_data.get("offer_type")

                if not offer_type:
                    raise serializers.ValidationError({
                        "details": "offer_type is missing"
                    })

                if offer_type in existing_details:
                    # Update existing detail
                    detail = existing_details[offer_type]
                    for attr, value in detail_data.items():
                        setattr(detail, attr, value)
                    detail.save()
                else:
                    # Create new detail if not found
                    DetailOffer.objects.create(offer=instance, **detail_data)

        return instance