from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom user manager for username-based authentication"""
    
    def create_user(self, username, name, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        user = self.model(username=username, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, name, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model for Villa Manager Hub
    Uses username as the username field
    """
    username = models.CharField(max_length=150, unique=True, verbose_name='Username')
    email = models.EmailField(blank=True, verbose_name='Email Address')
    name = models.CharField(max_length=255, verbose_name='Full Name')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Phone Number')
    
    objects = UserManager()
    
    # Use username field for authentication
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        return self.name or self.get_full_name()

