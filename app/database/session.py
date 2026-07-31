from supabase import create_client, Client

from app.core.config import settings


def get_supabase() -> Client:
    """Get Supabase client instance"""
    print(f"DEBUG: SUPABASE_URL = {settings.supabase_url}")
    print(f"DEBUG: SUPABASE_KEY = {settings.supabase_key[:20]}..." if settings.supabase_key else "DEBUG: SUPABASE_KEY = None")
    print(f"DEBUG: SUPABASE_SERVICE_ROLE_KEY = {settings.supabase_service_role_key[:20]}..." if settings.supabase_service_role_key else "DEBUG: SUPABASE_SERVICE_ROLE_KEY = None")
    
    if not settings.supabase_url or not settings.supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
    
    # Use service role key for backend operations (has full database access)
    key = settings.supabase_service_role_key if settings.supabase_service_role_key else settings.supabase_key
    print(f"DEBUG: Using key type = {'SERVICE_ROLE' if settings.supabase_service_role_key else 'PUBLIC'}")
    return create_client(settings.supabase_url, key)


# Global Supabase client (initialized lazily)
_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """Get or create Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = get_supabase()
    return _supabase_client
