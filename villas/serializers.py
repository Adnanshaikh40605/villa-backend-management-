from rest_framework import serializers
from .models import Villa


class VillaSerializer(serializers.ModelSerializer):
    """Serializer for Villa model"""
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Villa
        fields = [
            'id', 'name', 'location', 'max_guests', 'price_per_night',
            'status', 'image', 'description', 'amenities',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VillaListSerializer(serializers.ModelSerializer):
    """Simplified serializer for villa list"""
    
    class Meta:
        model = Villa
        fields = [
            'id', 'name', 'location', 'max_guests',
            'price_per_night', 'status', 'image'
        ]
