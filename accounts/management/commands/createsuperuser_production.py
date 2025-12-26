"""
Django management command to create a superuser for production
Usage: python manage.py createsuperuser_production
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import sys


class Command(BaseCommand):
    help = 'Creates a superuser for production deployment'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Superuser credentials
        USERNAME = 'adnan'
        NAME = 'Adnan'
        PASSWORD = 'villa4'
        
        try:
            # Check if user already exists
            if User.objects.filter(username=USERNAME).exists():
                self.stdout.write(self.style.SUCCESS(f'✅ User "{USERNAME}" already exists!'))
                
                # Update password in case it changed
                user = User.objects.get(username=USERNAME)
                user.set_password(PASSWORD)
                user.is_superuser = True
                user.is_staff = True
                user.save()
                
                self.stdout.write(self.style.SUCCESS(f'✅ Password and permissions updated for user "{USERNAME}"'))
            else:
                # Create new superuser
                user = User.objects.create_superuser(
                    username=USERNAME,
                    name=NAME,
                    password=PASSWORD
                )
                self.stdout.write(self.style.SUCCESS(f'✅ Superuser "{USERNAME}" created successfully!'))
            
            # Verify the user was created/updated correctly
            user.refresh_from_db()
            self.stdout.write(self.style.SUCCESS(f'\n📋 Superuser Details:'))
            self.stdout.write(f'   Username: {user.username}')
            self.stdout.write(f'   Name: {user.name}')
            self.stdout.write(f'   Is Superuser: {user.is_superuser}')
            self.stdout.write(f'   Is Staff: {user.is_staff}')
            self.stdout.write(f'   Is Active: {user.is_active}')
            
            self.stdout.write(self.style.SUCCESS(f'\n🔗 You can now login at the admin panel'))
            self.stdout.write(f'   Username: {USERNAME}')
            self.stdout.write(f'   Password: {PASSWORD}')
            
            return 0
            
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'❌ Database integrity error: {str(e)}'))
            return 1
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Unexpected error: {str(e)}'))
            self.stdout.write(self.style.ERROR(f'   Error type: {type(e).__name__}'))
            import traceback
            self.stdout.write(self.style.ERROR(f'   Traceback: {traceback.format_exc()}'))
            return 1
