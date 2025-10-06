"""
System settings management service
"""
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.db.models import SystemSettings
import json


class SettingCreate(BaseModel):
    setting_key: str
    setting_value: str
    setting_type: str = "string"
    description: Optional[str] = None


class SettingUpdate(BaseModel):
    setting_value: Optional[str] = None
    setting_type: Optional[str] = None
    description: Optional[str] = None


class SettingResponse(BaseModel):
    id: int
    setting_key: str
    setting_value: str
    setting_type: str
    description: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


def get_setting(db: Session, key: str) -> Optional[SystemSettings]:
    """Get a specific setting by key"""
    return db.query(SystemSettings).filter(
        SystemSettings.setting_key == key).first()


def get_setting_value(db: Session, key: str, default_value: Any = None) -> Any:
    """Get a setting value with type conversion"""
    setting = get_setting(db, key)
    if not setting:
        return default_value

    try:
        if setting.setting_type == "int":
            return int(setting.setting_value)
        elif setting.setting_type == "float":
            return float(setting.setting_value)
        elif setting.setting_type == "bool":
            return setting.setting_value.lower() in ("true", "1", "yes")
        elif setting.setting_type == "json":
            return json.loads(setting.setting_value)
        else:
            return setting.setting_value
    except (ValueError, json.JSONDecodeError):
        return default_value


def set_setting(db: Session, key: str, value: Any,
                setting_type: str = "string",
                description: Optional[str] = None) -> SystemSettings:
    """Set a setting value with automatic type detection"""
    # Convert value to string for storage
    if isinstance(value, (dict, list)):
        value_str = json.dumps(value)
        setting_type = "json"
    elif isinstance(value, bool):
        value_str = str(value).lower()
        setting_type = "bool"
    elif isinstance(value, (int, float)):
        value_str = str(value)
        setting_type = "int" if isinstance(value, int) else "float"
    else:
        value_str = str(value)

    # Check if setting exists
    existing_setting = get_setting(db, key)
    if existing_setting:
        existing_setting.setting_value = value_str
        existing_setting.setting_type = setting_type
        if description:
            existing_setting.description = description
        db.commit()
        db.refresh(existing_setting)
        return existing_setting
    else:
        # Create new setting
        new_setting = SystemSettings(
            setting_key=key,
            setting_value=value_str,
            setting_type=setting_type,
            description=description
        )
        db.add(new_setting)
        db.commit()
        db.refresh(new_setting)
        return new_setting


def get_all_settings(db: Session) -> Dict[str, Any]:
    """Get all settings as a dictionary"""
    settings = db.query(SystemSettings).all()
    result = {}

    for setting in settings:
        result[setting.setting_key] = get_setting_value(
            db, setting.setting_key)

    return result


def initialize_default_settings(db: Session):
    """Initialize default system settings"""
    default_settings = [
        ("default_priority", "normal", "string", "Default analysis priority level"),
        ("auto_delete_days", "7", "int", "Auto-delete uploads after N days"),
        ("email_notifications", "true", "bool", "Enable email notifications"),
        ("api_rate_limit", "100", "int", "API rate limit per minute"),
        ("max_file_size_mb", "100", "int", "Maximum file size in MB"),
        ("api_logging", "true", "bool", "Enable API request logging"),
        ("require_auth", "true", "bool", "Require authentication for uploads"),
        ("encrypt_files", "true", "bool", "Encrypt uploaded files"),
        ("session_timeout_minutes", "60", "int", "Session timeout in minutes"),
        ("analysis_timeout_seconds", "300", "int", "Analysis timeout in seconds"),
        ("max_concurrent_analyses", "5", "int", "Maximum concurrent analyses"),
        ("enable_adaptive_learning", "true", "bool", "Enable adaptive learning"),
    ]

    for key, value, setting_type, description in default_settings:
        existing = get_setting(db, key)
        if not existing:
            set_setting(db, key, value, setting_type, description)


def delete_setting(db: Session, key: str) -> bool:
    """Delete a setting"""
    setting = get_setting(db, key)
    if not setting:
        return False

    db.delete(setting)
    db.commit()
    return True
