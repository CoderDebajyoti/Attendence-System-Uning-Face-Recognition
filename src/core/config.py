# ==============================================================================
# Face Recognition Attendance System - Configuration Manager
# ==============================================================================

import os
from pathlib import Path
from dotenv import load_dotenv
from src.core.settings import AppSettings

class ConfigLoader:
    """
    Responsible for fetching config variables from active environments (.env file)
    and mapping them to a type-safe AppSettings object.
    """

    @classmethod
    def load_config(cls) -> AppSettings:
        """
        Loads .env values, performs error-tolerant type conversions,
        and builds the configuration model.
        """
        # Read the .env file if it exists locally
        load_dotenv()

        # Parse text parameters
        app_name = os.getenv("APP_NAME", "Face Recognition Attendance System")
        app_env = os.getenv("APP_ENV", "development")
        debug = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
        log_level = os.getenv("LOG_LEVEL", "INFO")
        database_url = os.getenv("DATABASE_URL", "sqlite:///database/app_database.db")
        camera_rtsp_url = os.getenv("CAMERA_RTSP_URL", "")
        secret_key = os.getenv("SECRET_KEY", "replace_with_a_secure_cryptographic_secret_key_in_production")

        # Safely convert numeric indicators
        try:
            camera_id = int(os.getenv("CAMERA_ID", "0"))
        except ValueError:
            camera_id = 0

        try:
            camera_fps_target = int(os.getenv("CAMERA_FPS_TARGET", "30"))
        except ValueError:
            camera_fps_target = 30

        try:
            recognition_threshold = float(os.getenv("RECOGNITION_THRESHOLD", "0.65"))
        except ValueError:
            recognition_threshold = 0.65

        try:
            cooldown_minutes = int(os.getenv("COOLDOWN_MINUTES", "30"))
        except ValueError:
            cooldown_minutes = 30

        try:
            target_image_count = int(os.getenv("TARGET_IMAGE_COUNT", "25"))
        except ValueError:
            target_image_count = 25

        # Build paths objects
        model_path = Path(os.getenv("MODEL_PATH", "models"))
        dataset_path = Path(os.getenv("DATASET_PATH", "database/datasets"))
        export_path = Path(os.getenv("EXPORT_PATH", "database/exports"))
        backup_path = Path(os.getenv("BACKUP_PATH", "database/backups"))

        return AppSettings(
            app_name=app_name,
            app_env=app_env,
            debug=debug,
            log_level=log_level,
            database_url=database_url,
            camera_id=camera_id,
            camera_rtsp_url=camera_rtsp_url,
            camera_fps_target=camera_fps_target,
            recognition_threshold=recognition_threshold,
            cooldown_minutes=cooldown_minutes,
            target_image_count=target_image_count,
            model_path=model_path,
            dataset_path=dataset_path,
            export_path=export_path,
            backup_path=backup_path,
            secret_key=secret_key
        )
