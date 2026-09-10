from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EduDrive CRM API"
    api_prefix: str = "/api/v1"
    debug: bool = True
    
    # TiDB Database Configuration
    tidb_host: str = ""
    tidb_port: int = 4000
    tidb_user: str = ""
    tidb_password: str = ""
    tidb_database: str = "edudrive_crm"
    tidb_ca_path: str = ""
    
    # JWT Configuration
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    allowed_origins: list[str] = ["http://localhost:3000", "https://edudrive-crm.onrender.com", "https://*.onrender.com"]
    frontend_url: str = "https://edudrive-crm.onrender.com"  # Frontend URL for payment callbacks
    
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
