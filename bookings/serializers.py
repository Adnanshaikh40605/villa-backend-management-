from rest_framework import serializers
from .models import Booking
from villas.serializers import VillaListSerializer


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model"""
    villa_details = VillaListSerializer(source='villa', read_only=True)
    nights = serializers.ReadOnlyField()
    pending_payment = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'villa', 'villa_details', 'client_name', 'client_phone',
            'client_email', 'check_in', 'check_out', 'status',
            'number_of_guests', 'notes', 'payment_status', 'booking_source',
            'total_payment', 'advance_payment', 'pending_payment', 'nights', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_payment', 'pending_payment', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Custom validation for bookings"""
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        
        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError({
                'check_out': 'Check-out date must be after check-in date.'
            })
        
        # Validate advance_payment if provided
        advance_payment = data.get('advance_payment')
        if advance_payment and advance_payment < 0:
            raise serializers.ValidationError({
                'advance_payment': 'Advance payment cannot be negative.'
            })
        
        # Check availability
        villa = data.get('villa')
        if villa and check_in and check_out:
            # Exclude current booking if updating
            exclude_id = self.instance.id if self.instance else None
            
            overlapping = Booking.objects.filter(
                villa=villa,
                check_in__lt=check_out,
                check_out__gt=check_in
            )
            
            if exclude_id:
                overlapping = overlapping.exclude(id=exclude_id)
            
            if overlapping.exists():
                raise serializers.ValidationError({
                    'check_in': 'Villa is not available for the selected dates.'
                })
        
        return data
    
    def create(self, validated_data):
        # Set created_by to current user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class BookingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for booking list"""
    villa = VillaListSerializer(read_only=True)
    pending_payment = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'villa', 'client_name', 'client_phone',
            'check_in', 'check_out', 'status', 'payment_status',
            'total_payment', 'advance_payment', 'pending_payment'
        ]
