from django.contrib import admin
from .models import Villa


@admin.register(Villa)
class VillaAdmin(admin.ModelAdmin):
    """Admin interface for Villa model"""
    list_display = ['name', 'location', 'max_guests', 'price_per_night', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'location']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location', 'status')
        }),
        ('Capacity & Pricing', {
            'fields': ('max_guests', 'price_per_night')
        }),
        ('Details', {
            'fields': ('description', 'amenities', 'image')
        }),
    )
