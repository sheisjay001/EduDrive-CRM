"""
Add a parent user account to the database via Supabase.
Run this to create the parent3@edudrive.demo user.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.session import get_supabase_client
from app.core.auth import get_password_hash


def add_parent_user():
    """Add a parent user account to Supabase."""
    print("Adding parent user to Supabase...")
    
    supabase = get_supabase_client()
    
    try:
        # First, check if the school exists
        school_result = supabase.table('schools').select('*').eq('slug', 'greenfield-college').execute()
        
        if not school_result.data:
            # Try to get any school
            all_schools = supabase.table('schools').select('*').execute()
            print(f"Total schools found: {len(all_schools.data) if all_schools.data else 0}")
            if all_schools.data:
                school = all_schools.data[0]
                print(f"School 'greenfield-college' not found. Using existing school: {school['name']} (slug: {school['slug']})")
            else:
                print("❌ No schools found in database. Creating a demo school...")
                # Create a demo school
                school_data = {
                    'name': 'Demo School',
                    'slug': 'demo-school',
                    'school_type': 'Secondary',
                    'primary_color': '#14213D'
                }
                school_result = supabase.table('schools').insert(school_data).execute()
                school = school_result.data[0]
                print(f"Created demo school: {school['name']}")
        else:
            school = school_result.data[0]
            print(f"Found school: {school['name']}")
        
        # Check if parent role exists
        role_result = supabase.table('roles').select('*').eq('school_id', school['id']).eq('name', 'parent').execute()
        
        if not role_result.data:
            # Create parent role
            role_data = {
                'school_id': school['id'],
                'name': 'parent',
                'permissions': ["view_children", "view_invoices", "create_tickets", "view_tickets"]
            }
            role_result = supabase.table('roles').insert(role_data).execute()
            parent_role = role_result.data[0]
            print(f"Created parent role: {parent_role['name']}")
        else:
            parent_role = role_result.data[0]
            print(f"Parent role already exists: {parent_role['name']}")
        
        # Check if parent user already exists
        user_result = supabase.table('users').select('*').eq('email', 'parent3@edudrive.demo').execute()
        
        if user_result.data:
            print("⚠️  Parent user 'parent3@edudrive.demo' already exists.")
            print(f"   User ID: {user_result.data[0]['id']}")
            return
        
        # Create parent user
        user_data = {
            'school_id': school['id'],
            'role_id': parent_role['id'],
            'full_name': 'Demo Parent',
            'email': 'parent3@edudrive.demo',
            'password_hash': get_password_hash("password123"),
            'status': 'active'
        }
        
        user_result = supabase.table('users').insert(user_data).execute()
        parent_user = user_result.data[0]
        
        print("\n✅ Parent user created successfully!")
        print(f"   Email: {parent_user['email']}")
        print(f"   Name: {parent_user['full_name']}")
        print(f"   Role: {parent_role['name']}")
        print(f"   Password: password123")
        print("\nLogin credentials:")
        print(f"   Email: parent3@edudrive.demo")
        print(f"   Password: password123")
        
    except Exception as e:
        print(f"❌ Error adding parent user: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    add_parent_user()
