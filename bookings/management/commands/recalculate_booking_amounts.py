from django.core.management.base import BaseCommand
from bookings.models import Booking


class Command(BaseCommand):
    help = 'Recalculate total_amount for all existing bookings based on current pricing configuration'

    def handle(self, *args, **options):
        bookings = Booking.objects.select_related('villa').all()
        updated_count = 0

        for booking in bookings:
            old_amount = booking.total_amount
            
            # Force recalculation by calling save
            # The save() method will automatically recalculate based on villa pricing
            booking.save()
            
            if old_amount != booking.total_amount:
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated booking #{booking.id}: ₹{old_amount or 0} → ₹{booking.total_amount}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully recalculated {updated_count} out of {bookings.count()} bookings'
            )
        )
