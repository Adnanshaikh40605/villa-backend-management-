from rest_framework import serializers
from .models import Villa, GlobalSpecialDay


class GlobalSpecialDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSpecialDay
        fields = ['id', 'name', 'day', 'month', 'year', 'created_at']
        read_only_fields = ['id', 'created_at']


class VillaSerializer(serializers.ModelSerializer):
    """Serializer for Villa model"""
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Villa
        fields = [
            'id', 'name', 'location', 'max_guests', 'price_per_night',
            'weekend_price', 'special_day_price', 'weekend_days', 'special_prices',
            'status', 'image', 'description', 'amenities',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_weekend_days(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Weekend days must be a list of integers.")
        for day in value:
            if not isinstance(day, int) or day < 0 or day > 6:
               raise serializers.ValidationError("Days must be integers between 0 (Mon) and 6 (Sun).")
        return value


class VillaListSerializer(serializers.ModelSerializer):
    """Simplified serializer for villa list"""
    
    class Meta:
        model = Villa
        fields = [
            'id', 'name', 'location', 'max_guests',
            'price_per_night', 'weekend_price', 'special_day_price', 
            'weekend_days', 'status', 'image'
        ]
