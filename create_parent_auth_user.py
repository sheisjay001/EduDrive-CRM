"""
Create a parent user in Supabase Auth and link to custom users table.
Run this to create the parent3@edudrive.demo user in Supabase Auth.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.session import get_supabase_client


def create_parent_auth_user():
    """Create a parent user in Supabase Auth and link to custom tables."""
    print("Creating parent user in Supabase Auth...")
    
    supabase = get_supabase_client()
    
    try:
        # First, check if the school exists
        school_result = supabase.table('schools').select('*').eq('slug', 'demo-school').execute()
        
        if not school_result.data:
            # Try to get any school
            all_schools = supabase.table('schools').select('*').execute()
            if all_schools.data:
                school = all_schools.data[0]
                print(f"Using existing school: {school['name']} (slug: {school['slug']})")
            else:
                print("❌ No schools found in database. Creating a demo school...")
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
        
        # Create user in Supabase Auth
        email = "parent3@edudrive.demo"
        password = "password123"
        
        print(f"\nCreating user in Supabase Auth: {email}")
        
        try:
            # Try to sign up the user in Supabase Auth
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": "Demo Parent"
                    }
                }
            })
            
            print(f"✅ User created in Supabase Auth")
            print(f"   User ID: {auth_response.user.id}")
            print(f"   Email: {auth_response.user.email}")
            
            supabase_user_id = auth_response.user.id
            
        except Exception as auth_error:
            # User might already exist in Auth, try to get the user
            print(f"Auth signup failed (user might exist): {auth_error}")
            print("Trying to get existing user from Auth...")
            
            # We can't directly query Auth users, so we'll check if the user exists in our custom table
            # and assume they exist in Auth if they do
            user_result = supabase.table('users').select('*').eq('email', email).execute()
            if user_result.data:
                supabase_user_id = user_result.data[0]['id']
                print(f"Found existing user in custom table with ID: {supabase_user_id}")
            else:
                print("❌ User not found in Auth or custom table. Please create manually in Supabase dashboard.")
                return
        
        # Check if user exists in custom users table
        user_result = supabase.table('users').select('*').eq('email', email).execute()
        
        if not user_result.data:
            # Create user in custom users table
            from app.core.auth import get_password_hash
            user_data = {
                'id': supabase_user_id,  # Use the same ID as Supabase Auth
                'school_id': school['id'],
                'role_id': parent_role['id'],
                'full_name': 'Demo Parent',
                'email': email,
                'password_hash': get_password_hash(password),
                'status': 'active'
            }
            user_result = supabase.table('users').insert(user_data).execute()
            print(f"✅ Created user in custom users table")
        else:
            # Update existing user to use the Supabase Auth ID
            existing_user = user_result.data[0]
            if existing_user['id'] != supabase_user_id:
                print(f"Deleting old user record and recreating with Supabase Auth ID")
                # Delete old record
                supabase.table('users').delete().eq('email', email).execute()
                # Insert new record with correct ID
                from app.core.auth import get_password_hash
                user_data = {
                    'id': supabase_user_id,
                    'school_id': school['id'],
                    'role_id': parent_role['id'],
                    'full_name': 'Demo Parent',
                    'email': email,
                    'password_hash': get_password_hash(password),
                    'status': 'active'
                }
                supabase.table('users').insert(user_data).execute()
                print(f"✅ Recreated user in custom users table with correct ID")
            else:
                print(f"User already exists in custom users table with correct ID")
        
        # Verify user exists in custom users table before creating role mapping
        verify_user = supabase.table('users').select('*').eq('id', supabase_user_id).execute()
        if not verify_user.data:
            print(f"❌ ERROR: User {supabase_user_id} not found in users table after insert")
            return
        else:
            print(f"✅ Verified user exists in users table: {verify_user.data[0]['email']}")
        
        # Check if user role mapping exists
        role_mapping_result = supabase.table('user_roles').select('*').eq('user_id', supabase_user_id).execute()
        
        if not role_mapping_result.data:
            # Create user role mapping
            role_mapping_data = {
                'user_id': supabase_user_id,
                'role': 'parent',
                'school_id': school['id']
            }
            supabase.table('user_roles').insert(role_mapping_data).execute()
            print(f"✅ Created user role mapping")
        else:
            print(f"User role mapping already exists")
        
        print("\n✅ Parent user setup complete!")
        print(f"\nLogin credentials:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"\nAfter login, user will be redirected to: /parent/dashboard")
        
    except Exception as e:
        print(f"❌ Error creating parent user: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    create_parent_auth_user()
