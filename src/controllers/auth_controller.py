# ==============================================================================
# Face Recognition Attendance System - Authentication Controller
# ==============================================================================

import logging
from src.services.auth_service import AuthService
from src.core.models import User

logger = logging.getLogger("app.controllers")

class AuthController:
    """
    Coordinates frontend authentication views requests and forwards them to AuthService.
    """
    def __init__(self) -> None:
        self.auth_service = AuthService.get_instance()

    def login(self, username: str, password: str) -> User | None:
        """
        Processes login authentication validation.
        """
        if not username or not password:
            return None
        return self.auth_service.authenticate_user(username, password)

    def register_first_admin(self, username: str, password: str) -> User | None:
        """
        Registers the initial system administrator during first-run setups.
        """
        if self.auth_service.has_users():
            logger.warning("Attempted to register first admin, but database already contains registered users.")
            return None
        if not username or not password:
            return None
        return self.auth_service.create_user(username, password, role="Admin")

    def system_has_users(self) -> bool:
        """
        Identifies whether user accounts exist in database.
        """
        return self.auth_service.has_users()
