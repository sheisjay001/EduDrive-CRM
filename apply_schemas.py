"""
Script to apply all SQL schema files to Supabase via the Supabase REST API.
This executes SQL directly through Supabase's SQL endpoint.
"""
import os
import glob
import requests
from pathlib import Path
from app.core.config import settings

# Add requests to requirements if not present

def execute_sql_via_rest(sql_content, schema_name):
    """Execute SQL via Supabase REST API"""
    url = f"{settings.supabase_url}/rest/v1/rpc/exec_sql"
    
    headers = {
        'apikey': settings.supabase_service_role_key,
        'Authorization': f'Bearer {settings.supabase_service_role_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    try:
        response = requests.post(url, json={'sql': sql_content}, headers=headers)
        if response.status_code in [200, 201]:
            print(f"✓ Successfully applied {schema_name}")
            return True
        else:
            print(f"✗ Error applying {schema_name}: HTTP {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"✗ Error applying {schema_name}: {str(e)}")
        return False

def apply_schema_files():
    """Apply all schema SQL files to Supabase"""
    # Get all schema files
    schema_files = glob.glob("*_schema.sql")
    schema_files.sort()
    
    print(f"Found {len(schema_files)} schema files to apply")
    print("=" * 60)
    
    success_count = 0
    failed_files = []
    
    for schema_file in schema_files:
        schema_name = schema_file.replace('_schema.sql', '')
        print(f"\nApplying {schema_name}...")
        
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Execute the SQL
            if execute_sql_via_rest(sql_content, schema_name):
                success_count += 1
            else:
                failed_files.append(schema_name)
                
        except Exception as e:
            print(f"✗ Error reading {schema_file}: {str(e)}")
            failed_files.append(schema_name)
    
    print("\n" + "=" * 60)
    print(f"Summary: {success_count}/{len(schema_files)} schemas applied successfully")
    
    if failed_files:
        print(f"\nFailed schemas: {', '.join(failed_files)}")
    
    return success_count == len(schema_files)

if __name__ == "__main__":
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("Applying SQL schema files to Supabase...")
    print("=" * 60)
    
    success = apply_schema_files()
    
    if success:
        print("\n✓ All schemas applied successfully!")
    else:
        print("\n✗ Some schemas failed to apply. Check the errors above.")
