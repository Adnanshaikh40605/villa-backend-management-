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
    
    PAYMENT_METHOD_CHOICES = [
        ('online', 'Online'),
        ('cash', 'Cash'),
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
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True,
        verbose_name='Payment Method'
    )
    total_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Total Payment (INR)',
        help_text='Auto-calculated total booking amount'
    )
    advance_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        verbose_name='Advance Payment (INR)',
        help_text='Amount paid in advance'
    )
    override_total_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Override Total Payment (INR)',
        help_text='Manual override for total payment. If set, ignores auto-calculation.'
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
    
    def _get_price_for_date(self, date):
        """
        Get the price for a specific date based on pricing priority.
        Priority: Special Date Price > Weekend Price > Base Price
        
        Args:
            date: The date to get the price for
            
        Returns:
            Decimal: The price for the given date
        """
        from decimal import Decimal
        from datetime import datetime
        
        # Priority 1: Check special date pricing
        if self.villa.special_prices:
            try:
                special_prices = self.villa.special_prices
                if isinstance(special_prices, list):
                    for special_price in special_prices:
                        if not isinstance(special_price, dict):
                            continue
                            
                        # Get start and end dates
                        start_date_str = special_price.get('start_date')
                        end_date_str = special_price.get('end_date')
                        price = special_price.get('price')
                        
                        if not all([start_date_str, end_date_str, price]):
                            continue
                        
                        # Parse dates
                        try:
                            if isinstance(start_date_str, str):
                                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                            else:
                                start_date = start_date_str
                                
                            if isinstance(end_date_str, str):
                                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                            else:
                                end_date = end_date_str
                            
                            # Check if current date falls within this special price range
                            if start_date <= date <= end_date:
                                return Decimal(str(price))
                        except (ValueError, TypeError):
                            # Skip invalid date formats
                            continue
            except (TypeError, AttributeError):
                # If special_prices is not a valid list, skip
                pass
        
        # Priority 2: Check weekend pricing
        day_of_week = date.weekday()  # 0=Monday, 6=Sunday
        is_configured_weekend = (
            self.villa.weekend_days and 
            day_of_week in self.villa.weekend_days
        )
        
        if is_configured_weekend and self.villa.weekend_price:
            return self.villa.weekend_price
        
        # Priority 3: Base price
        return self.villa.price_per_night
    
    def save(self, *args, **kwargs):
        """
        Save the booking and handle total payment calculation.
        
        If override_total_payment is set:
        - Use the override value as total_payment
        
        Otherwise, auto-calculate based on villa pricing:
        1. Special Date Price (from villa.special_prices)
        2. Weekend Price (if day is in villa.weekend_days)
        3. Base Price (villa.price_per_night)
        
        Payment Calculation:
        - total_payment: Override or auto-calculated from pricing
        - advance_payment: User-entered amount
        - pending_payment: Calculated as (total_payment - advance_payment)
        """
        if self.check_in and self.check_out and self.villa:
            from decimal import Decimal
            from datetime import timedelta
            
            # Check if manual override is provided
            if self.override_total_payment is not None:
                # Use the override value
                self.total_payment = self.override_total_payment
            else:
                # Auto-calculate from villa pricing
                total = Decimal('0')
                current_date = self.check_in
                
                # Iterate through each night of the stay
                while current_date < self.check_out:
                    # Get price for this specific date using priority hierarchy
                    price = self._get_price_for_date(current_date)
                    total += price
                    current_date += timedelta(days=1)
                
                self.total_payment = total
        
        # Validate advance_payment doesn't exceed total_payment
        if self.advance_payment and self.total_payment:
            from decimal import Decimal
            advance = self.advance_payment or Decimal('0')
            if advance > self.total_payment:
                raise ValidationError({
                    'advance_payment': 'Advance payment cannot exceed total payment.'
                })
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def nights(self):
        """Calculate number of nights"""
        if self.check_in and self.check_out:
            return (self.check_out - self.check_in).days
        return 0
    
    @property
    def pending_payment(self):
        """Calculate pending payment"""
        from decimal import Decimal
        total = self.total_payment or Decimal('0')
        advance = self.advance_payment or Decimal('0')
        return total - advance
    
    @property
    def auto_calculated_price(self):
        """
        Calculate what the total price would be based on villa pricing,
        regardless of override. Returns price breakdown by date.
        """
        if not (self.check_in and self.check_out and self.villa):
            return None
        
        from decimal import Decimal
        from datetime import timedelta
        
        breakdown = {
            'total': Decimal('0'),
            'nights': [],
            'base_nights': 0,
            'weekend_nights': 0,
            'special_nights': 0,
        }
        
        current_date = self.check_in
        
        while current_date < self.check_out:
            price = self._get_price_for_date(current_date)
            breakdown['total'] += price
            
            # Determine price type for this night
            price_type = 'base'
            
            # Check if it's a special day
            if self.villa.special_prices:
                try:
                    from datetime import datetime
                    special_prices = self.villa.special_prices
                    if isinstance(special_prices, list):
                        for special_price in special_prices:
                            if not isinstance(special_price, dict):
                                continue
                            
                            start_date_str = special_price.get('start_date')
                            end_date_str = special_price.get('end_date')
                            sp_price = special_price.get('price')
                            
                            if not all([start_date_str, end_date_str, sp_price]):
                                continue
                            
                            try:
                                if isinstance(start_date_str, str):
                                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                                else:
                                    start_date = start_date_str
                                    
                                if isinstance(end_date_str, str):
                                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                                else:
                                    end_date = end_date_str
                                
                                if start_date <= current_date <= end_date:
                                    price_type = 'special'
                                    break
                            except (ValueError, TypeError):
                                continue
                except (TypeError, AttributeError):
                    pass
            
            # Check if it's a weekend (only if not already special)
            if price_type != 'special':
                day_of_week = current_date.weekday()
                is_configured_weekend = (
                    self.villa.weekend_days and 
                    day_of_week in self.villa.weekend_days
                )
                if is_configured_weekend and self.villa.weekend_price:
                    price_type = 'weekend'
            
            # Add to breakdown
            breakdown['nights'].append({
                'date': current_date.isoformat(),
                'price': float(price),
                'type': price_type
            })
            
            if price_type == 'base':
                breakdown['base_nights'] += 1
            elif price_type == 'weekend':
                breakdown['weekend_nights'] += 1
            elif price_type == 'special':
                breakdown['special_nights'] += 1
            
            current_date += timedelta(days=1)
        
        breakdown['total'] = float(breakdown['total'])
        return breakdown

