"""
Configuration settings for Music Police API using Pydantic BaseSettings
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Set


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Music Police - AI Compliance Engine"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENV: str = "dev"

    # Database settings
    DATABASE_URL: str = "postgresql://musicpolice_user:musicpolice_password@localhost:5432/musicpolice_db"

    # File upload settings
    UPLOAD_DIR: Path = Path("uploads")
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: Set[str] = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}

    # ML Model settings
    SIMILARITY_THRESHOLD: float = 0.7
    BIAS_DETECTION_ENABLED: bool = True
    COPYRIGHT_CHECK_ENABLED: bool = True

    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.UPLOAD_DIR.mkdir(exist_ok=True)
        Path("static").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)


settings = Settings()
