"""
Test PostgreSQL database connection using Railway credentials
"""
import psycopg2
from psycopg2 import OperationalError

# Railway PostgreSQL credentials
DB_CONFIG = {
    'dbname': 'railway',
    'user': 'postgres',
    'password': 'TfJvwkrSvCryRtkKuTelBBbEWDLWrhOa',
    'host': 'turntable.proxy.rlwy.net',  # Public host for external access
    'port': '57771'
}

def test_connection():
    """Test database connection"""
    print("=" * 60)
    print("Testing PostgreSQL Database Connection")
    print("=" * 60)
    print(f"\nConnection Details:")
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  Port: {DB_CONFIG['port']}")
    print(f"  Database: {DB_CONFIG['dbname']}")
    print(f"  User: {DB_CONFIG['user']}")
    print("\nAttempting to connect...\n")
    
    try:
        # Attempt to connect
        connection = psycopg2.connect(**DB_CONFIG)
        
        # Create a cursor
        cursor = connection.cursor()
        
        # Execute a simple query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print("✅ CONNECTION SUCCESSFUL!")
        print(f"\nPostgreSQL Version:")
        print(f"  {db_version[0]}")
        
        # Get database size
        cursor.execute("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as size;
        """)
        db_size = cursor.fetchone()
        print(f"\nDatabase Size: {db_size[0]}")
        
        # List tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"\nExisting Tables ({len(tables)}):")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("\nNo tables found (database is empty - migrations needed)")
        
        # Close cursor and connection
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 60)
        print("Database connection test completed successfully!")
        print("=" * 60)
        
        return True
        
    except OperationalError as e:
        print("❌ CONNECTION FAILED!")
        print(f"\nError: {e}")
        print("\nPossible issues:")
        print("  1. Network connectivity problem")
        print("  2. Incorrect credentials")
        print("  3. Database server is down")
        print("  4. Firewall blocking the connection")
        print("\n" + "=" * 60)
        return False
    
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    test_connection()
