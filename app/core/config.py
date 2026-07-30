from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EduDrive CRM API"
    api_prefix: str = "/api/v1"
    debug: bool = True
    database_url: str = "sqlite:///./edudrive.db"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    allowed_origins: list[str] = ["http://localhost:3000", "https://edudrive-crm.onrender.com", "https://*.onrender.com"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
