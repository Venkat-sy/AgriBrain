from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


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
        default=["http://localhost:3000", "http://localhost:8080", "*"],
        description="Allowed CORS origins"
    )
    
    # ML Models
    SOIL_CLASSIFIER_MODEL_PATH: str = "models/soil_classifier.pkl"
    DISEASE_DETECTOR_MODEL_PATH: str = "models/disease_detector.pkl"
    RAINFALL_FORECAST_MODEL_PATH: str = "models/rainfall_forecast.pkl"
    
    # External APIs
    IMD_API_KEY: Optional[str] = None
    OPENWEATHER_API_KEY: Optional[str] = None
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


@lru_cache()
def get_settings() -> Settings:
    return settings


# Dependency for FastAPI
def get_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()