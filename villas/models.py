from django.db import models
from django.core.validators import MinValueValidator


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Villa'
        verbose_name_plural = 'Villas'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def is_active(self):
        return self.status == 'active'

