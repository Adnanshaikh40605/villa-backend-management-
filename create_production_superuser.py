"""
Script to create a superuser in production
Usage: railway run python create_production_superuser.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Superuser credentials
USERNAME = 'adnan'
NAME = 'Adnan'
PASSWORD = 'villa4'

# Check if user already exists
if User.objects.filter(username=USERNAME).exists():
    print(f"✅ User '{USERNAME}' already exists!")
    user = User.objects.get(username=USERNAME)
    # Update password in case it changed
    user.set_password(PASSWORD)
    user.save()
    print(f"✅ Password updated for user '{USERNAME}'")
else:
    # Create new superuser
    user = User.objects.create_superuser(
        username=USERNAME,
        name=NAME,
        password=PASSWORD
    )
    print(f"✅ Superuser '{USERNAME}' created successfully!")

print(f"\n📋 Login credentials:")
print(f"   Username: {USERNAME}")
print(f"   Password: {PASSWORD}")
print(f"\n🔗 Admin URL: https://villa-backend-management-production.up.railway.app/admin/")
