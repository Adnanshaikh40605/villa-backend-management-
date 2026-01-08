from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from villas.models import Villa


class Booking(models.Model):
    """
    Represents a villa booking or blocked period
    """
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('blocked', 'Blocked'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('advance', 'Advance Paid'),
        ('full', 'Fully Paid'),
    ]
    
    SOURCE_CHOICES = [
        ('call', 'Phone Call'),
        ('whatsapp', 'WhatsApp'),
        ('website', 'Website'),
        ('other', 'Other'),
    ]
    
    villa = models.ForeignKey(
        Villa,
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name='Villa'
    )
    client_name = models.CharField(max_length=255, verbose_name='Client Name')
    client_phone = models.CharField(max_length=20, verbose_name='Client Phone')
    client_email = models.EmailField(blank=True, verbose_name='Client Email')
    check_in = models.DateField(verbose_name='Check-in Date')
    check_out = models.DateField(verbose_name='Check-out Date')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='booked',
        verbose_name='Status'
    )
    number_of_guests = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Number of Guests'
    )
    notes = models.TextField(blank=True, verbose_name='Notes')
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name='Payment Status'
    )
    booking_source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        null=True,
        blank=True,
        verbose_name='Booking Source'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Total Amount (INR)'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_bookings',
        verbose_name='Created By'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-check_in']
        indexes = [
            models.Index(fields=['villa', 'check_in', 'check_out']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.villa.name} - {self.client_name} ({self.check_in} to {self.check_out})"
    
    def clean(self):
        """Validate booking data"""
        if self.check_in and self.check_out:
            if self.check_out <= self.check_in:
                raise ValidationError({
                    'check_out': 'Check-out date must be after check-in date.'
                })
        
        # Phone is now optional for all bookings
        # Number of guests validation removed - users can enter any number of guests
    
    def save(self, *args, **kwargs):
        # Auto-calculate total amount based on villa pricing configuration
        if self.check_in and self.check_out and self.villa:
            from decimal import Decimal
            from datetime import timedelta
            
            total = Decimal('0')
            current_date = self.check_in
            
            # Iterate through each night of the stay
            while current_date < self.check_out:
                day_of_week = current_date.weekday()  # 0=Monday, 6=Sunday
                
                # Check if this day is configured as a weekend day for this villa
                is_configured_weekend = (
                    self.villa.weekend_days and 
                    day_of_week in self.villa.weekend_days
                )
                
                # Determine the price for this night
                # Priority: Weekend price (if configured) > Base price
                if is_configured_weekend and self.villa.weekend_price:
                    price = self.villa.weekend_price
                else:
                    price = self.villa.price_per_night
                
                total += price
                current_date += timedelta(days=1)
            
            self.total_amount = total
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def nights(self):
        """Calculate number of nights"""
        if self.check_in and self.check_out:
            return (self.check_out - self.check_in).days
        return 0

