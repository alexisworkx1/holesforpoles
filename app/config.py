import os
import secrets
from typing import Dict, Any, Optional
from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application settings
    APP_NAME: str = "Holes For Poles"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # CORS settings
    ALLOWED_ORIGINS: str = "*"
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    DATABASE_CONNECT_ARGS: Dict[str, Any] = {}
    
    @validator("DATABASE_CONNECT_ARGS")
    def set_connect_args(cls, v: Dict[str, Any], values: Dict[str, Any]) -> Dict[str, Any]:
        """Set connect_args for SQLite database."""
        db_url = values.get("DATABASE_URL", "")
        if "sqlite" in db_url:
            return {"check_same_thread": False}
        return {}
    
    # JWT related settings
    JWT_ALGORITHM: str = "HS256"
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


# Create instance of settings
settings = Settings()

