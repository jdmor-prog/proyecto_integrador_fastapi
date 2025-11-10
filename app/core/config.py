from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    app_name: str = "Project Name API"
    database_url: str = "sqlite:///./project.db"
    auto_create_tables: bool = True
    # CORS configuration
    cors_allow_origins: List[str] = ["*"]
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    cors_allow_credentials: bool = True

    # JWT security configuration
    jwt_secret: str = "CHANGE_ME_SUPER_SECRET_KEY"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()