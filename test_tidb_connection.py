"""Test TiDB database connection"""
import pymysql
import ssl
from app.core.config import settings

def test_connection():
    try:
        # SSL configuration for TiDB Cloud (always required)
        ssl_context = ssl.create_default_context()
        if settings.tidb_ca_path:
            ssl_context.load_verify_locations(cafile=settings.tidb_ca_path)
        else:
            # For TiDB Cloud, use SSL without custom CA
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        # Test TiDB connection
        connection = pymysql.connect(
            host=settings.tidb_host,
            port=settings.tidb_port,
            user=settings.tidb_user,
            password=settings.tidb_password,
            database=settings.tidb_database,
            ssl={'ssl_context': ssl_context}
        )
        
        print("✓ Successfully connected to TiDB")
        
        # Test query
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✓ TiDB Version: {version[0]}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✓ Found {len(tables)} tables in database")
            
        connection.close()
        print("✓ Connection test passed")
        return True
        
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
