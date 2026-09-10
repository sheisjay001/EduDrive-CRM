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
    return get_db()
