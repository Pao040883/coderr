from rest_framework import serializers
from ..models import Offer, DetailOffer
from django.db.models import Min
from rest_framework.reverse import reverse


class UserMixin(serializers.Serializer):
    """Mixin to add a user field with structured output."""
    
    user_details = serializers.SerializerMethodField()

    def get_user_details(self, obj):
        return {
            "first_name": obj.user.first_name if obj.user else "",
            "last_name": obj.user.last_name if obj.user else "",
            "email": obj.user.email if obj.user else "",
        }



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
        request = self.context.get('request')
        return [
            {"id": detail.id, "url": reverse("offer-detail", args=[detail.id], request=request)}
            for detail in obj.details.all()
        ]

    def get_min_price(self, obj):
        return obj.details.aggregate(Min("price"))["price__min"]

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(Min("delivery_time_in_days"))["delivery_time_in_days__min"]

    def validate_details(self, value):
        if len(value) != 3:
            raise serializers.ValidationError({"detail": ["3 Details erforderlich"]})
        
        offer_types = {detail['offer_type'] for detail in value}
        required_type = {'basic', 'standard', 'premium'}

        if offer_types != required_type:
            raise serializers.ValidationError({"detail": ["1 Basic, 1 Standard und 1 Premium Details erforderlich"]})
        
        return value

class OfferDetailSerializer(serializers.ModelSerializer):     
    class Meta:
        model = DetailOffer
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days', 
            'price', 'features', 'offer_type'
        ]

class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'image', 'description', 
            'created_at', 'updated_at', 'details'
        ]

    def validate_details(self, value):
        """Validiert Details nur bei der Erstellung eines neuen Offers"""
        if self.instance is None:  # Nur für create, nicht für update
            if len(value) != 3:
                raise serializers.ValidationError({"detail": ["3 Details erforderlich"]})

            offer_types = {detail['offer_type'] for detail in value}
            required_types = {'basic', 'standard', 'premium'}

            if offer_types != required_types:
                raise serializers.ValidationError({"detail": ["1 Basic, 1 Standard und 1 Premium Details erforderlich"]})

        return value
    
    def create(self, validated_data):
        """ Erstellt ein neues Angebot und speichert die Details """
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            DetailOffer.objects.create(offer=offer, **detail_data)

        return offer
    
    def update(self, instance, validated_data):
        """ Aktualisiert das bestehende Angebot und seine Details """
        details_data = validated_data.pop('details', None)

        # Aktualisiere die Offer-Felder
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Falls Details übergeben wurden, aktualisiere sie
        if details_data is not None:
            existing_details = {detail.offer_type: detail for detail in instance.details.all()}
            
            for detail_data in details_data:
                offer_type = detail_data.get("offer_type")

                if offer_type in existing_details:
                    # Falls das Detail existiert, aktualisiere es
                    detail = existing_details[offer_type]
                    for attr, value in detail_data.items():
                        setattr(detail, attr, value)
                    detail.save()
                else:
                    # Falls das Detail nicht existiert, erstelle es neu
                    DetailOffer.objects.create(offer=instance, **detail_data)

        return instance