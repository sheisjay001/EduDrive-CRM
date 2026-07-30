from supabase import create_client, Client

from app.core.config import settings


def get_supabase() -> Client:
    """Get Supabase client instance"""
    return create_client(settings.supabase_url, settings.supabase_key)


# Global Supabase client
supabase: Client = get_supabase()
