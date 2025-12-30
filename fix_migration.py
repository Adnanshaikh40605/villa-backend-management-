"""
Simple script to apply the problematic migration by temporarily allowing null usernames
"""
from django.db import connection

# Add username column allowing NULL first
with connection.cursor() as cursor:
    try:
        # Add username column as nullable first
        cursor.execute("""
            ALTER TABLE accounts_user ADD COLUMN username VARCHAR(150) NULL;
        """)
        print("✓ Added username column")
        
        # Update existing users with email-based usernames
        cursor.execute("""
            UPDATE accounts_user 
            SET username = LOWER(SUBSTR(email, 1, INSTR(email, '@') - 1))
            WHERE username IS NULL;
        """)
        print("✓ Added usernames to existing users")
        
        # Now make it unique and not null
        cursor.execute("""
            CREATE UNIQUE INDEX accounts_user_username_unique ON accounts_user (username);
        """)
        print("✓ Made username unique")
        
        print("\n✅ Database updated successfully!")
        print("Now run: py manage.py migrate")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nIf column already exists, try:")
        print("py manage.py migrate accounts --fake")
