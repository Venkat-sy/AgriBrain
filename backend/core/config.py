from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AgriSim"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database - Use SQLite for development if PostgreSQL not available
    DATABASE_URL: str = Field(
        default="sqlite:///./agrisim_dev.db",
        description="Database connection URL (SQLite for dev, PostgreSQL for prod)"
    )

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )

    # JWT Authentication (RS256 asymmetric)
    JWT_PRIVATE_KEY_PATH: str = Field(
        default="keys/private_key.pem",
        description="Path to RS256 private key for signing tokens"
    )
    JWT_PUBLIC_KEY_PATH: str = Field(
        default="keys/public_key.pem",
        description="Path to RS256 public key for verifying tokens"
    )
    JWT_ALGORITHM: str = "RS256"
    JWT_ISSUER: str = "agribrain-api"
    JWT_AUDIENCE: str = "agribrain-clients"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Rate Limiting (7 tiers)
    RATE_LIMIT_ENABLED: bool = True
    # Tier configs: requests per window
    RL_AUTH_STRICT_RPM: int = 10      # login, register, password reset
    RL_API_STANDARD_RPM: int = 60     # standard API endpoints
    RL_API_BURST_RPM: int = 120       # burst allowance for authenticated users
    RL_ANONYMOUS_RPM: int = 20        # unauthenticated requests
    RL_ADMIN_RPM: int = 300           # admin endpoints
    RL_WEBSOCKET_RPM: int = 50        # WebSocket connections
    RL_WEBHOOK_RPM: int = 100         # webhook endpoints

    # Session Management
    SESSION_TTL_MINUTES: int = 30
    SESSION_MAX_IDLE_MINUTES: int = 15
    SESSION_CLEANUP_CRON: str = "0 */6 * * *"  # every 6 hours

    # ML Models
    SOIL_CLASSIFIER_MODEL_PATH: str = "models/soil_classifier.pkl"
    DISEASE_DETECTOR_MODEL_PATH: str = "models/disease_detector.pkl"
    RAINFALL_FORECAST_MODEL_PATH: str = "models/rainfall_forecast.pkl"

    # External APIs
    IMD_API_KEY: Optional[str] = None
    OPENWEATHER_API_KEY: Optional[str] = None
    WEATHER_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None

    # Upstash Redis
    UPSTASH_REDIS_REST_URL: Optional[str] = None
    UPSTASH_REDIS_REST_TOKEN: Optional[str] = None

    # Crop Database
    CROPS_MASTER_YAML_PATH: str = "data/crops_master.yaml"
    CROPS_MASTER_JSON_PATH: str = "data/crops_master.json"

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )


# Global settings instance
settings = Settings()


@lru_cache()
def get_settings() -> Settings:
    return settings


# Database engine and session factory
def _get_database_url() -> str:
    """Get database URL with postgres:// -> postgresql:// fix for SQLAlchemy 1.4+"""
    url = settings.DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def _create_engine():
    """Create SQLAlchemy engine with appropriate connect args"""
    database_url = _get_database_url()
    is_sqlite = database_url.startswith("sqlite")

    connect_args = {"check_same_thread": False} if is_sqlite else {}

    return create_engine(database_url, connect_args=connect_args)


# Create engine and session factory at module level
engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()