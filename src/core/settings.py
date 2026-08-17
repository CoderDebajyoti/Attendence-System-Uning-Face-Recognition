# ==============================================================================
# Face Recognition Attendance System - Application Settings Schema
# ==============================================================================

from dataclasses import dataclass, field
from pathlib import Path
from src.core import constants

@dataclass
class AppSettings:
    """
    Container class representing application-wide configuration parameters.
    Ensures type checking on parameters parsed from local files or .env variables.
    """
    
    # Global Settings
    app_name: str = "Face Recognition Attendance System"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Database connection parameters
    database_url: str = "sqlite:///database/app_database.db"

    # Camera settings
    camera_id: int = 0
    camera_rtsp_url: str = ""
    camera_fps_target: int = constants.DEFAULT_CAMERA_FPS

    # Recognition limits
    recognition_threshold: float = constants.DEFAULT_RECOGNITION_THRESHOLD
    cooldown_minutes: int = constants.DEFAULT_COOLDOWN_MINUTES
    target_image_count: int = constants.DEFAULT_TARGET_IMAGE_COUNT
    attendance_auto_mode: bool = constants.DEFAULT_ATTENDANCE_AUTO_MODE


    # Storage paths
    model_path: Path = field(default_factory=lambda: Path("models"))
    dataset_path: Path = field(default_factory=lambda: Path("database/datasets"))
    export_path: Path = field(default_factory=lambda: Path("database/exports"))
    backup_path: Path = field(default_factory=lambda: Path("database/backups"))

    # Security
    secret_key: str = "replace_with_a_secure_cryptographic_secret_key_in_production"
