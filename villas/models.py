from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Villa(models.Model):
    """
    Represents a villa property available for booking
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Maintenance'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name='Villa Name')
    location = models.CharField(max_length=255, verbose_name='Location')
    max_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Maximum Guests'
    )
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Price Per Night (INR)'
    )
    weekend_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        verbose_name='Weekend Price (INR)'
    )
    special_day_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        verbose_name='Special Day Price (INR)'
    )
    weekend_days = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Weekend Days (0=Mon, 6=Sun)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    image = models.ImageField(
        upload_to='villas/',
        blank=True,
        null=True,
        verbose_name='Villa Image'
    )
    description = models.TextField(blank=True, verbose_name='Description')
    amenities = models.JSONField(default=list, blank=True, verbose_name='Amenities')
    special_prices = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Special Prices Config',
        help_text='List of special pricing rules (ranges or specific dates)'
    )
    order = models.IntegerField(default=0, verbose_name='Display Order')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Villa'
        verbose_name_plural = 'Villas'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def is_active(self):
        return self.status == 'active'


class GlobalSpecialDay(models.Model):
    """
    Represents a global special day configuration (e.g. Christmas, New Year)
    """
    name = models.CharField(max_length=100)
    day = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(31)])
    month = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Year (Optional)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['month', 'day']
        unique_together = ['day', 'month', 'year']
        
    def __str__(self):
        date_str = f"{self.day}/{self.month}"
        if self.year:
            date_str += f"/{self.year}"
        return f"{self.name} ({date_str})"

