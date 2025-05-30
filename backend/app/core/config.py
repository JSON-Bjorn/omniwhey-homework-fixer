from typing import Any, Dict, List, Optional
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Omniwhey Homework Fixer"
    ENVIRONMENT: str = "development"  # development, staging, production

    # Database settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    DATABASE_URI: Optional[str] = None

    # Database connection pool settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800  # 30 minutes
    DB_ECHO: bool = False
    DB_PRE_PING: bool = True

    # Database maintenance settings
    ENABLE_DB_MAINTENANCE: bool = Field(
        True, description="Enable automated database maintenance tasks"
    )
    DB_MAINTENANCE_INTERVAL: int = Field(
        24, description="Interval in hours between database maintenance runs"
    )

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Construct the database URI."""
        if self.DATABASE_URI:
            return self.DATABASE_URI
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # JWT Token settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # AI API settings
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Security settings
    ALLOWED_HOSTS: List[str] = ["*"]

    # Rate limiting
    RATE_LIMIT_DEFAULT: int = (
        10  # per minute (lowered from 100 to be easier to test)
    )
    RATE_LIMIT_AI_ENDPOINTS: int = 5  # per minute

    # Email settings
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_PORT: Optional[int] = 587
    MAIL_SERVER: Optional[str] = None
    MAIL_FROM_NAME: Optional[str] = None
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path("logs")
    LOG_FILENAME: str = "app.log"

    # Model config
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


# Create settings instance
settings = Settings()
