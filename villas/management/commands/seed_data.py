from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from villas.models import Villa
from bookings.models import Booking
from datetime import date, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with initial data for development'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # Create superuser if not exists
        if not User.objects.filter(email='admin@villa.com').exists():
            User.objects.create_superuser(
                email='admin@villa.com',
                name='Villa Admin',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('✓ Created superuser (admin@villa.com / admin123)'))
        else:
            self.stdout.write('✓ Superuser already exists')
        
        # Create villas if not exist
        villas_data = [
            {
                'name': 'SOLE VILLA',
                'location': 'Beachfront, East Wing',
                'max_guests': 10,
                'price_per_night': 12000,
                'status': 'active',
            },
            {
                'name': 'SEQUEL VILLA',
                'location': 'Garden View, West Wing',
                'max_guests': 8,
                'price_per_night': 10000,
                'status': 'active',
            },
            {
                'name': 'BITWIXT VILLA',
                'location': 'Poolside, Central',
                'max_guests': 6,
                'price_per_night': 8000,
                'status': 'active',
            },
            {
                'name': 'FOUNTAIN VILLA',
                'location': 'Hilltop, North Wing',
                'max_guests': 12,
                'price_per_night': 15000,
                'status': 'active',
            },
        ]
        
        for villa_data in villas_data:
            villa, created = Villa.objects.get_or_create(
                name=villa_data['name'],
                defaults=villa_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created villa: {villa.name}'))
            else:
                self.stdout.write(f'✓ Villa already exists: {villa.name}')
        
        # Create sample bookings
        if not Booking.objects.exists():
            today = date.today()
            admin_user = User.objects.filter(email='admin@villa.com').first()
            
            bookings_data = [
                {
                    'villa': Villa.objects.get(name='SOLE VILLA'),
                    'client_name': 'Amit Verma',
                    'client_phone': '9876543210',
                    'check_in': today + timedelta(days=1),
                    'check_out': today + timedelta(days=4),
                    'status': 'booked',
                    'number_of_guests': 4,
                    'notes': 'Pool side request',
                    'payment_status': 'advance',
                    'booking_source': 'whatsapp',
                    'created_by': admin_user,
                },
                {
                    'villa': Villa.objects.get(name='SEQUEL VILLA'),
                    'client_name': 'Priya Sharma',
                    'client_phone': '9876543211',
                    'check_in': today,
                    'check_out': today + timedelta(days=2),
                    'status': 'booked',
                    'number_of_guests': 6,
                    'payment_status': 'full',
                    'booking_source': 'call',
                    'created_by': admin_user,
                },
                {
                    'villa': Villa.objects.get(name='BITWIXT VILLA'),
                    'client_name': 'Owner Block',
                    'client_phone': '',
                    'check_in': today + timedelta(days=5),
                    'check_out': today + timedelta(days=7),
                    'status': 'blocked',
                    'notes': 'Owner personal use',
                    'created_by': admin_user,
                },
            ]
            
            for booking_data in bookings_data:
                Booking.objects.create(**booking_data)
                self.stdout.write(self.style.SUCCESS(f'✓ Created booking for {booking_data["client_name"]}'))
        else:
            self.stdout.write('✓ Sample bookings already exist')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
