from rest_framework import serializers
from ..models import Review

# Serializer for creating, retrieving, and updating Review objects
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review  # Specifies the model this serializer is based on
        fields = [
            'id',             # Unique identifier of the review
            'business_user',  # The user (business) that the review is written about
            'reviewer',       # The user who created the review
            'rating',         # Numerical rating given by the reviewer
            'description',    # Optional text describing the review
            'created_at',     # Timestamp when the review was created
            'updated_at'      # Timestamp when the review was last updated
        ]