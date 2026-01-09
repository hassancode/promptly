"""Application configuration management"""
import os
from typing import Optional
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://promptly:promptly_dev_password@localhost:5432/promptly"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    SESSION_TTL_SECONDS: int = 604800  # 7 days
    SESSION_COOKIE_NAME: str = "promptly_session"

    # AI Provider API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None

    # Provider Configuration
    ENABLED_PROVIDERS: str = "openai,claude,gemini,perplexity,google_ai,huggingface"

    # Application
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change_this_in_production_very_important"
    DEBUG: bool = True

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


# Global settings instance
settings = Settings()


def validate_required_vars():
    """Validate that required environment variables are set"""
    errors = []

    if settings.ENVIRONMENT == "production":
        if settings.SECRET_KEY == "change_this_in_production_very_important":
            errors.append("SECRET_KEY must be changed in production")
        if not settings.DEBUG == False:
            errors.append("DEBUG must be False in production")

    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")


# Validate on import
validate_required_vars()
