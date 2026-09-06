import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Intelligent Land Record Digitization and Validation System"
    ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api"

    # JWT Authentication
    JWT_SECRET_KEY: str = "super-secret-land-record-jwt-token-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Database
    DATABASE_URL: str = "sqlite:///./land_records.db"

    # Storage
    STORAGE_DIR: str = "./storage"

    # LLM Abstraction
    LLM_PROVIDER: str = "gemini"
    LLM_API_KEY: Optional[str] = ""
    LLM_MODEL: str = "gemini-1.5-flash"

    # Thresholds
    HIGH_CONFIDENCE_THRESHOLD: float = 0.85
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.60

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure storage subdirectories exist
os.makedirs(os.path.join(settings.STORAGE_DIR, "originals"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "processed"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "ocr"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "samples"), exist_ok=True)
