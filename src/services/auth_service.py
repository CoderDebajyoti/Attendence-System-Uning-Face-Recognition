# ==============================================================================
# Face Recognition Attendance System - Authentication Service
# ==============================================================================

import bcrypt
import logging
from datetime import datetime
from src.core.database import get_session
from src.core.models import User

logger = logging.getLogger("app.security")

class AuthService:
    """
    Handles user registry verification, password hashing, and authentication credentials validations.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def hash_password(self, password: str) -> str:
        """
        Hashes a plaintext password using bcrypt.
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verifies a plaintext password against a stored bcrypt hash.
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    def authenticate_user(self, username: str, password: str) -> User | None:
        """
        Validates username and password, returning the User object if successful.
        """
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username, User.is_active == True).first()
            if user and self.verify_password(password, user.password_hash):
                # Detach user from active transaction session to prevent closing references
                session.expunge(user)
                return user
            return None
        except Exception as e:
            logger.error(f"User authentication error: {e}")
            return None
        finally:
            session.close()

    def create_user(self, username: str, password: str, role: str = "Admin") -> User | None:
        """
        Creates a new user with a hashed password in the database.
        """
        session = get_session()
        try:
            # Check if user already exists
            existing = session.query(User).filter(User.username == username).first()
            if existing:
                logger.warning(f"Registration aborted: user '{username}' already exists.")
                return None

            password_hash = self.hash_password(password)
            user = User(
                username=username,
                password_hash=password_hash,
                role=role,
                is_active=True,
                created_at=datetime.utcnow()
            )
            session.add(user)
            session.commit()
            
            # Detach object before closing session
            session.refresh(user)
            session.expunge(user)
            logger.info(f"Successfully registered user '{username}' with role '{role}'.")
            return user
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create user '{username}': {e}")
            return None
        finally:
            session.close()

    def has_users(self) -> bool:
        """
        Checks if there is at least one active user in the database.
        Used to identify if first-run setup is required.
        """
        session = get_session()
        try:
            count = session.query(User).count()
            return count > 0
        except Exception as e:
            logger.error(f"Error querying users count: {e}")
            return False
        finally:
            session.close()
