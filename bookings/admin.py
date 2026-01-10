from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface for Booking model"""
    list_display = [
        'id', 'villa', 'client_name', 'check_in', 'check_out',
        'status', 'payment_status', 'total_payment', 'advance_payment', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'booking_source', 'check_in']
    search_fields = ['client_name', 'client_phone', 'client_email']
    ordering = ['-check_in']
    date_hierarchy = 'check_in'
    
    fieldsets = (
        ('Villa & Dates', {
            'fields': ('villa', 'check_in', 'check_out', 'status')
        }),
        ('Client Information', {
            'fields': ('client_name', 'client_phone', 'client_email', 'number_of_guests')
        }),
        ('Booking Details', {
            'fields': ('payment_status', 'booking_source', 'total_payment', 'advance_payment', 'notes')
        }),
        ('System Information', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['total_payment', 'created_by']
