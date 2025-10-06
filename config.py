"""
Configuration settings for Music Police API
"""
import os
from pathlib import Path


class Settings:
    # Application settings
    APP_NAME = "Music Police - AI Compliance Engine"
    VERSION = "1.0.0"
    DEBUG = True

    # Database settings
    DATABASE_URL = "postgresql://musicpolice_user:musicpolice_password@localhost:5432/musicpolice_db"

    # File upload settings
    UPLOAD_DIR = Path("uploads")
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}

    # ML Model settings
    SIMILARITY_THRESHOLD = 0.7
    BIAS_DETECTION_ENABLED = True
    COPYRIGHT_CHECK_ENABLED = True

    # Server settings
    HOST = "127.0.0.1"
    PORT = 8000

    def __init__(self):
        # Create necessary directories
        self.UPLOAD_DIR.mkdir(exist_ok=True)
        Path("static").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)


settings = Settings()
