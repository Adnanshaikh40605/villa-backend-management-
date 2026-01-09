import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from villas.models import Villa
from villas.serializers import VillaSerializer

def test_special_price_update():
    try:
        villa = Villa.objects.get(id=2)
        print(f"Current Special Prices: {villa.special_prices}")

        # Construct payload with new special price
        current_prices = villa.special_prices or []
        new_price = {
            "start_date": "2026-01-27",
            "end_date": "2026-01-27",
            "price": 8000.00,
            "name": "Republic Day Special"
        }
        
        # Append new price to list
        updated_prices = current_prices + [new_price]
        
        payload = {
            "special_prices": updated_prices
        }
        
        print("\nTesting Serializer Update...")
        serializer = VillaSerializer(instance=villa, data=payload, partial=True)
        
        if serializer.is_valid():
            print("Serializer is valid.")
            saved_villa = serializer.save()
            print(f"Saved Special Prices: {saved_villa.special_prices}")
            
            # Verify persistence
            villa.refresh_from_db()
            print(f"Refreshed DB Special Prices: {villa.special_prices}")
        else:
            print("Serializer Errors:")
            print(serializer.errors)

    except Villa.DoesNotExist:
        print("Villa ID 2 not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_special_price_update()
