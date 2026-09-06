"""
Create a parent user in Supabase Auth and link to custom tables.
Run this to create the parent3@edudrive.demo user in Supabase Auth.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2
from urllib.parse import urlparse
from app.core.config import settings


def get_postgres_connection():
    """Get direct PostgreSQL connection using service role credentials."""
    # Hardcode the DATABASE_URL for this script
    database_url = "postgresql://postgres:Soteria2003@db.zdnxmgevzhaqksgllyzg.supabase.co:5432/postgres"
    
    return psycopg2.connect(database_url)


def create_parent_auth_user():
    """Create a parent user using direct PostgreSQL connection."""
    print("Creating parent user using direct PostgreSQL connection...")
    
    try:
        conn = get_postgres_connection()
        conn.autocommit = True
        cursor = conn.cursor()
        
        supabase_user_id = "7788b872-8a1b-4dfb-b03f-0311ce0b2082"
        email = "parent3@edudrive.demo"
        
        print(f"Using Supabase Auth user ID: {supabase_user_id}")
        
        # Get school ID
        cursor.execute("SELECT id FROM schools WHERE slug = 'demo-school' LIMIT 1")
        school_row = cursor.fetchone()
        if not school_row:
            print("❌ School not found")
            return
        school_id = school_row[0]
        print(f"✅ Found school ID: {school_id}")
        
        # Get parent role ID
        cursor.execute("SELECT id FROM roles WHERE school_id = %s AND name = 'parent' LIMIT 1", (school_id,))
        role_row = cursor.fetchone()
        if not role_row:
            print("❌ Parent role not found")
            return
        parent_role_id = role_row[0]
        print(f"✅ Found parent role ID: {parent_role_id}")
        
        # Delete existing user
        cursor.execute("DELETE FROM users WHERE email = %s", (email,))
        print(f"✅ Deleted existing user record")
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (id, school_id, role_id, full_name, email, password_hash, status)
            VALUES (%s, %s, %s, 'Demo Parent', %s, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyW9iW5J5q6m', 'active')
        """, (supabase_user_id, school_id, parent_role_id, email))
        print(f"✅ Inserted user into users table")
        
        # Verify user exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE id = %s", (supabase_user_id,))
        count = cursor.fetchone()[0]
        print(f"✅ User count in users table: {count}")
        
        if count == 0:
            print("❌ User not found after insert!")
            return
        
        # Delete existing role mapping
        cursor.execute("DELETE FROM user_roles WHERE user_id = %s", (supabase_user_id,))
        print(f"✅ Deleted existing role mapping")
        
        # Insert role mapping
        cursor.execute("""
            INSERT INTO user_roles (user_id, role, school_id)
            VALUES (%s, 'parent', %s)
        """, (supabase_user_id, school_id))
        print(f"✅ Inserted role mapping")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Parent user setup complete!")
        print(f"\nLogin credentials:")
        print(f"   Email: {email}")
        print(f"   Password: password123")
        print(f"\nAfter login, user will be redirected to: /parent/dashboard")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    create_parent_auth_user()
