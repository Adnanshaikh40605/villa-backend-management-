from django.core.management.base import BaseCommand
from bookings.models import Booking
from villas.models import Villa
from datetime import timedelta
import calendar

class Command(BaseCommand):
    help = 'Recalculate prices for bookings with 0 or null total_payment'

    def handle(self, *args, **options):
        # Find bookings with 0 or null total_payment
        bookings = Booking.objects.filter(total_payment__isnull=True) | Booking.objects.filter(total_payment=0)
        
        count = bookings.count()
        self.stdout.write(f"Found {count} bookings with 0 or null payment.")
        
        fixed_count = 0
        for booking in bookings:
            try:
                # We need to calculate price based on booking dates and villa
                # Note: This uses CURRENT villa prices, which might be different from when booked.
                # But for repair, this is the best approximation.
                
                total = 0
                current_date = booking.check_in
                
                while current_date < booking.check_out:
                    price = self.get_price_for_date(booking.villa, current_date)
                    total += price
                    current_date += timedelta(days=1)
                
                booking.total_payment = total
                # If advance is 0, leave it 0 or assume full payment? 
                # Let's set Pending = Total - Advance (handled by serializer typically, here we update DB field if it existed, but pending is dynamic in frontend usually. 
                # Wait, model doesn't store pending. It calculates it.
                # Actually, models.Booking doesn't have pending_payment field?
                # Checked models.py: It has payment_status, total_payment, advance_payment.
                # Pending is calculated.
                
                booking.save()
                self.stdout.write(f"Fixed Booking #{booking.id}: {booking.total_payment}")
                fixed_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fixing booking {booking.id}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"Successfully fixed {fixed_count} bookings"))

    def get_price_for_date(self, villa, date):
        # 1. Special Prices
        if villa.special_prices:
            try:
                for sp in villa.special_prices:
                    if not isinstance(sp, dict): continue
                    
                    # Basic date parsing/comparison logic
                    # Assuming strings YYYY-MM-DD
                    start = sp.get('start_date')
                    end = sp.get('end_date')
                    price = sp.get('price')
                    
                    if start and end and price:
                        if start <= str(date) <= end:
                            return float(price)
            except:
                pass

        # 2. Weekend Pricing
        # Python weekday: Mon=0, Sun=6
        # Villa weekend_days: array of ints
        if villa.weekend_days and villa.weekend_price:
            if date.weekday() in villa.weekend_days:
                return float(villa.weekend_price)
        
        # 3. Base Price
        return float(villa.price_per_night)
