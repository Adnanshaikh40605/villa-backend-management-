"""
Script to create the local PostgreSQL database for development
Run this script once before starting the Django server
"""
import psycopg2
from psycopg2 import sql
from decouple import config
import sys
import os

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception:
        # Fallback if encoding setup fails
        pass

# Database configuration
DB_NAME = config('LOCAL_DB_NAME', default='villa_manage')
DB_USER = config('LOCAL_DB_USER', default='postgres')
DB_PASSWORD = config('LOCAL_DB_PASSWORD', default='adnan12')
DB_HOST = config('LOCAL_DB_HOST', default='localhost')
DB_PORT = config('LOCAL_DB_PORT', default='5432')

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (using 'postgres' database as default)
        print(f"Connecting to PostgreSQL server at {DB_HOST}:{DB_PORT}...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'  # Connect to default postgres database
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        print(f"Checking if database '{DB_NAME}' exists...")
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_NAME,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"[SUCCESS] Database '{DB_NAME}' already exists!")
            cursor.close()
            conn.close()
            return True
        
        # Create database
        print(f"Creating database '{DB_NAME}'...")
        # Use sql.Identifier to safely quote database name (handles spaces)
        cursor.execute(
            sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(DB_NAME)
            )
        )
        print(f"[SUCCESS] Database '{DB_NAME}' created successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"[ERROR] Connection error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check if the host, port, username, and password are correct")
        print("3. Verify PostgreSQL service is started")
        return False
    except psycopg2.Error as e:
        print(f"[ERROR] Database error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Local PostgreSQL Database Creation Script")
    print("=" * 60)
    print()
    
    if create_database():
        print()
        print("=" * 60)
        print("[SUCCESS] Next steps:")
        print("1. Run migrations:     py manage.py migrate")
        print("2. Create superuser:   py manage.py createsuperuser")
        print("3. Start server:       py manage.py runserver")
        print("=" * 60)
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("[ERROR] Failed to create database")
        print("=" * 60)
        sys.exit(1)
