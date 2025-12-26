"""
Script to create a superuser in production
Usage: Run this from Railway Shell UI:
       1. Railway → Service → Shell
       2. python create_production_superuser.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {str(e)}")
    sys.exit(1)

from django.contrib.auth import get_user_model

User = get_user_model()

# Superuser credentials
USERNAME = 'adnan'
NAME = 'Adnan'
PASSWORD = 'villa4'

try:
    # Check if user already exists
    if User.objects.filter(username=USERNAME).exists():
        print(f"✅ User '{USERNAME}' already exists!")
        user = User.objects.get(username=USERNAME)
        
        # Update password and ensure superuser permissions
        user.set_password(PASSWORD)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        
        print(f"✅ Password and permissions updated for user '{USERNAME}'")
    else:
        # Create new superuser
        user = User.objects.create_superuser(
            username=USERNAME,
            name=NAME,
            password=PASSWORD
        )
        print(f"✅ Superuser '{USERNAME}' created successfully!")
    
    # Verify the user
    user.refresh_from_db()
    print(f"\n📋 Superuser Details:")
    print(f"   Username: {user.username}")
    print(f"   Name: {user.name}")
    print(f"   Is Superuser: {user.is_superuser}")
    print(f"   Is Staff: {user.is_staff}")
    print(f"   Is Active: {user.is_active}")
    
    print(f"\n📋 Login credentials:")
    print(f"   Username: {USERNAME}")
    print(f"   Password: {PASSWORD}")
    print(f"\n🔗 Admin URL: https://villa-backend-management-production.up.railway.app/admin/")
    
except Exception as e:
    print(f"❌ Error creating superuser: {str(e)}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    print(f"   Traceback: {traceback.format_exc()}")
    sys.exit(1)

