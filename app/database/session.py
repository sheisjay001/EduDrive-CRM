import pymysql
from pymysql.cursors import DictCursor
import ssl

from app.core.config import settings


def get_tidb_connection():
    """Get TiDB database connection"""
    try:
        # SSL configuration for TiDB Cloud (always required)
        ssl_context = ssl.create_default_context()
        if settings.tidb_ca_path:
            ssl_context.load_verify_locations(cafile=settings.tidb_ca_path)
        else:
            # For TiDB Cloud, use SSL without custom CA
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        connection = pymysql.connect(
            host=settings.tidb_host,
            port=settings.tidb_port,
            user=settings.tidb_user,
            password=settings.tidb_password,
            database=settings.tidb_database,
            cursorclass=DictCursor,
            ssl={'ssl_context': ssl_context},
            autocommit=False
        )
        print(f"DEBUG: Connected to TiDB at {settings.tidb_host}:{settings.tidb_port}")
        return connection
    except Exception as e:
        print(f"ERROR: Failed to connect to TiDB: {e}")
        raise ValueError(f"TiDB connection failed: {e}")


# Global TiDB connection (initialized lazily)
_tidb_connection = None


def get_db():
    """Get or create TiDB database connection"""
    global _tidb_connection
    if _tidb_connection is None or not _tidb_connection.open:
        _tidb_connection = get_tidb_connection()
    return _tidb_connection


def close_db():
    """Close database connection"""
    global _tidb_connection
    if _tidb_connection and _tidb_connection.open:
        _tidb_connection.close()
        _tidb_connection = None


# Compatibility alias for existing code
def get_supabase_client():
    """Alias for get_db for backward compatibility during migration"""
    db = get_db()
    
    # Create a mock object that mimics Supabase client structure
    # to prevent crashes during migration
    class MockSupabaseClient:
        def __init__(self, connection):
            self.connection = connection
            self.auth = MockAuth()
        
        def table(self, table_name):
            return MockTable(self.connection, table_name)
    
    class MockAuth:
        def sign_up(self, data):
            raise HTTPException(status_code=501, detail="Signup endpoint not yet migrated to TiDB. Use /schools/register instead.")
        
        def reset_password_email(self, email):
            # Mock implementation - just return success
            return None
        
        def sign_in_with_password(self, data):
            raise HTTPException(status_code=501, detail="Auth endpoint not yet migrated to TiDB. Use /auth/login instead.")
    
    class MockTable:
        def __init__(self, connection, table_name):
            self.connection = connection
            self.table_name = table_name
        
        def insert(self, data):
            raise HTTPException(status_code=501, detail=f"Table insert for {self.table_name} not yet migrated to TiDB")
        
        def select(self, *columns):
            raise HTTPException(status_code=501, detail=f"Table select for {self.table_name} not yet migrated to TiDB")
        
        def update(self, data):
            raise HTTPException(status_code=501, detail=f"Table update for {self.table_name} not yet migrated to TiDB")
        
        def delete(self):
            raise HTTPException(status_code=501, detail=f"Table delete for {self.table_name} not yet migrated to TiDB")
    
    from fastapi import HTTPException
    return MockSupabaseClient(db)
