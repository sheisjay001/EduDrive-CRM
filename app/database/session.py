from supabase import create_client, Client

from app.core.config import settings


def get_supabase() -> Client:
    """Get Supabase client instance"""
    print(f"DEBUG: SUPABASE_URL = {settings.supabase_url}")
    print(f"DEBUG: SUPABASE_KEY = {settings.supabase_key[:20]}..." if settings.supabase_key else "DEBUG: SUPABASE_KEY = None")
    
    if not settings.supabase_url or not settings.supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
    return create_client(settings.supabase_url, settings.supabase_key)


# Global Supabase client (initialized lazily)
_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """Get or create Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = get_supabase()
    return _supabase_client
