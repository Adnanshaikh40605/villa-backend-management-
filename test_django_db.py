"""
Test Django database connection using manage.py
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['DATABASE_URL'] = 'postgresql://postgres:TfJvwkrSvCryRtkKuTelBBbEWDLWrhOa@turntable.proxy.rlwy.net:57771/railway'

django.setup()

from django.db import connection
from django.core.management import call_command

def test_django_db():
    """Test Django database connection"""
    print("=" * 60)
    print("Testing Django Database Connection")
    print("=" * 60)
    
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print("\n✅ Django database connection successful!")
            print(f"\nPostgreSQL Version: {version[0]}")
            
            # Check if migrations are needed
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'django_%'
            """)
            django_tables = cursor.fetchall()
            
            if django_tables:
                print(f"\n✅ Django tables found ({len(django_tables)} tables)")
                print("Database appears to be migrated.")
            else:
                print("\n⚠️  No Django tables found")
                print("You need to run: python manage.py migrate")
        
        print("\n" + "=" * 60)
        print("Django database test completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Django database connection failed!")
        print(f"Error: {e}")
        print("\n" + "=" * 60)

if __name__ == "__main__":
    test_django_db()
