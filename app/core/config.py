"""
Application configuration management using Pydantic.
Install: pip install pydantic-settings
"""
from pydantic import Field, field_validator, model_validator, ConfigDict
from pydantic_settings import BaseSettings
from typing import Optional, Any
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Get the project root directory (where .env file is located)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application settings with Pydantic validation and type checking."""
    
    # ==================== Database Configuration ====================
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL database connection string",
        examples=["postgresql://user:pass@localhost:5432/dbname"]
    )
    
    # ==================== JWT Authentication Configuration ====================
    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="JWT signing secret key, minimum 32 characters"
    )
    ALGORITHM: str = Field(
        default="HS256",
        pattern="^HS256|HS384|HS512|RS256$",
        description="JWT signing algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        ge=1,
        le=1440,
        description="Access token expiration time in minutes (max 24 hours)"
    )
    
    # ==================== AWS S3 Configuration ====================
    AWS_ACCESS_KEY_ID: Optional[str] = Field(
        default=None,
        description="AWS access key ID"
    )
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(
        default=None,
        description="AWS secret access key"
    )
    AWS_REGION: str = Field(
        default="us-east-1",
        description="AWS region"
    )
    S3_BUCKET_NAME: Optional[str] = Field(
        default=None,
        description="S3 bucket name for resume storage"
    )
    
    # ==================== OpenAI API Configuration ====================
    OPENAI_API_KEY: str = Field(
        ...,
        min_length=1,
        description="OpenAI API key (should start with 'sk-' in production)"
    )
    
    # ==================== Application Configuration ====================
    DEBUG: bool = Field(
        default=False,
        description="Debug mode flag"
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        pattern="^DEBUG|INFO|WARNING|ERROR|CRITICAL$",
        description="Logging level"
    )
    APP_NAME: str = Field(
        default="AI Job Matching",
        description="Application name"
    )
    
    # ==================== Redis/Celery Configuration ====================
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string for Celery broker"
    )
    
    # ==================== Pydantic Configuration ====================
    model_config = ConfigDict(
        env_file=str(ENV_FILE),  # Use absolute path to .env file
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        validate_default=True,
    )
    
    # ==================== Custom Validators ====================
    
    @model_validator(mode='after')
    def validate_secret_key_in_production(self) -> 'Settings':
        """Validate that SECRET_KEY is not the default placeholder value in production."""
        if "change-this" in self.SECRET_KEY.lower():
            if not self.DEBUG:
                raise ValueError(
                    "Please change the default SECRET_KEY in production! "
                    "Generate a new one: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )
            else:
                logger.warning("⚠️  Using default SECRET_KEY. Please change it before deploying to production!")
        
        return self
    
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith(("postgresql://", "sqlite://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL or SQLite connection string")
        return v
    
    # ==================== Computed Properties ====================
    
    def is_production(self) -> bool:
        """Check if the application is running in production mode."""
        return not self.DEBUG
    
    def validate_s3_config(self) -> bool:
        """Validate S3 configuration completeness."""
        s3_fields = [
            self.AWS_ACCESS_KEY_ID,
            self.AWS_SECRET_ACCESS_KEY,
            self.S3_BUCKET_NAME
        ]
        
        configured_count = sum(1 for field in s3_fields if field)
        
        if configured_count == 0:
            # No S3 configuration provided
            if self.is_production():
                logger.error("S3 configuration is required in production environment")
                raise ValueError("Production environment requires complete S3 configuration")
            else:
                logger.warning("S3 not configured. Resume upload functionality will be disabled.")
                return False
        elif configured_count == 3:
            # All S3 fields configured
            logger.info("S3 configuration is complete")
            return True
        else:
            # Partial S3 configuration
            missing = []
            if not self.AWS_ACCESS_KEY_ID:
                missing.append("AWS_ACCESS_KEY_ID")
            if not self.AWS_SECRET_ACCESS_KEY:
                missing.append("AWS_SECRET_ACCESS_KEY")
            if not self.S3_BUCKET_NAME:
                missing.append("S3_BUCKET_NAME")
            
            raise ValueError(f"Incomplete S3 configuration. Missing: {', '.join(missing)}")
    
    def model_post_init(self, __context) -> None:
        """Post-initialization validation."""
        # Validate S3 configuration
        try:
            self.validate_s3_config()
        except ValueError as e:
            if self.is_production():
                raise
            logger.warning(str(e))
        
        # Log configuration info
        logger.info(f"Application configuration loaded: {self.APP_NAME}")
        logger.info(f"Running mode: {'Production' if self.is_production() else 'Development'}")
        logger.info(f"Log level: {self.LOG_LEVEL}")


# ==================== Global Settings Instance ====================
try:
    settings = Settings()
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise
