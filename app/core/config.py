"""
Application configuration settings
"""

from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import secrets


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "VoltageGPU"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="production", env="ENVIRONMENT")
    
    # API Configuration
    API_V1_STR: str = "/v1"
    BASE_URL: str = "https://api.voltagegpu.com"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://voltagegpu.com",
        "https://www.voltagegpu.com",
        "https://api.voltagegpu.com"
    ]
    
    # Database
    DATABASE_URL: Optional[str] = None
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Backend Provider Configuration (Hidden from users)
    BACKEND_API_URL: str = Field(
        default="https://api.celiumcompute.ai/v1",
        description="Backend provider API URL"
    )
    BACKEND_API_KEY: Optional[str] = Field(None, env="BACKEND_API_KEY")
    
    # Pricing Configuration
    PRICING_MARKUP: float = Field(
        default=1.85, 
        description="Markup multiplier for pricing (1.85 = 85% markup)"
    )
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 1000
    RATE_LIMIT_PERIOD: int = 60  # seconds
    RATE_LIMIT_BURST: int = 100
    
    # Stripe Payment
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = True
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@voltagegpu.com"
    
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "voltagegpu-assets"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/voltagegpu.log"
    
    # GPU Configuration
    SUPPORTED_GPU_TYPES: List[str] = [
        "RTX_4090", "RTX_4080", "RTX_4070",
        "RTX_3090", "RTX_3080", "RTX_3070",
        "A100", "A40", "A30", "A10",
        "H100", "H200",
        "L40", "L4",
        "T4", "V100"
    ]
    
    SUPPORTED_REGIONS: List[str] = [
        "us-east-1", "us-west-1", "us-central-1",
        "eu-west-1", "eu-central-1",
        "ap-northeast-1", "ap-southeast-1"
    ]
    
    # Default Instance Configuration
    DEFAULT_INSTANCE_IMAGE: str = "pytorch:latest"
    DEFAULT_INSTANCE_DISK_SIZE: int = 100  # GB
    DEFAULT_INSTANCE_MEMORY: int = 32  # GB
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: Optional[str]) -> Optional[str]:
        if v and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
