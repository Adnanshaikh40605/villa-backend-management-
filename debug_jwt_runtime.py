import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

print("--- JWT SETTINGS DEBUG ---")
print(f"JWT_ACCESS_TOKEN_LIFETIME (min): {settings.JWT_ACCESS_TOKEN_LIFETIME_MINUTES}")
print(f"JWT_REFRESH_TOKEN_LIFETIME (min): {settings.JWT_REFRESH_TOKEN_LIFETIME_MINUTES}")
print(f"SIMPLE_JWT.ACCESS_TOKEN_LIFETIME: {settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']}")
print(f"SIMPLE_JWT.REFRESH_TOKEN_LIFETIME: {settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']}")
print(f"SIMPLE_JWT.ROTATE_REFRESH_TOKENS: {settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS']}")
print(f"SIMPLE_JWT.BLACKLIST_AFTER_ROTATION: {settings.SIMPLE_JWT['BLACKLIST_AFTER_ROTATION']}")
print("--- ENV CHECK ---")
print(f"Env 'JWT_ACCESS_TOKEN_LIFETIME': {os.environ.get('JWT_ACCESS_TOKEN_LIFETIME')}")
print("--------------------------")
