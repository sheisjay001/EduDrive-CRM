from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EduDrive CRM API"
    api_prefix: str = "/api/v1"
    debug: bool = True
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_role_key: str = ""
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    allowed_origins: list[str] = ["http://localhost:3000", "https://edudrive-crm.onrender.com", "https://*.onrender.com"]
    
    # Payment Gateway Configuration
    paystack_secret_key: str = ""
    paystack_public_key: str = ""
    flutterwave_secret_key: str = ""
    flutterwave_secret_hash: str = ""
    
    # Messaging API Configuration
    termii_api_key: str = ""
    termii_sender_id: str = "EduDrive"
    
    # Email Configuration (for future use)
    sendgrid_api_key: str = ""
    email_from_address: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
