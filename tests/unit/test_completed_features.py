# ==============================================================================
# Face Recognition Attendance System - Completed Features Unit Tests
# ==============================================================================

import pytest
import os
from pathlib import Path
from src.core.database import initialize_database, get_session
from src.core.models import User
from src.services.auth_service import AuthService
from src.controllers.auth_controller import AuthController
from src.services.face_detector_service import FaceDetectorService

@pytest.fixture(scope="module", autouse=True)
def setup_test_db() -> None:
    """
    Initializes a clean in-memory SQLite database specifically for test suites.
    """
    initialize_database("sqlite:///:memory:")
    yield

@pytest.fixture(autouse=True)
def clean_database() -> None:
    """
    Guarantees database records are reset between individual test runs.
    """
    session = get_session()
    try:
        session.query(User).delete()
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()

def test_password_hashing() -> None:
    """
    Verifies that AuthService hashes passwords using bcrypt and validates correctly.
    """
    auth = AuthService.get_instance()
    password = "secure_password123"
    
    # Hash password
    hashed = auth.hash_password(password)
    assert hashed != password
    assert len(hashed) > 10
    
    # Verify correct password
    assert auth.verify_password(password, hashed) is True
    
    # Verify incorrect password
    assert auth.verify_password("wrong_password", hashed) is False

def test_first_run_admin_registration() -> None:
    """
    Tests registering the initial system administrator on first-run setups.
    """
    controller = AuthController()
    
    # Database is empty, system_has_users should be False
    assert controller.system_has_users() is False
    
    # Register first administrator
    user = controller.register_first_admin("system_admin", "password123")
    assert user is not None
    assert user.username == "system_admin"
    assert user.role == "Admin"
    
    # Database now contains users
    assert controller.system_has_users() is True
    
    # Attempting to register another first admin should fail
    fail_user = controller.register_first_admin("second_admin", "password456")
    assert fail_user is None

def test_user_authentication_flow() -> None:
    """
    Verifies login credential matches and validation failures.
    """
    controller = AuthController()
    auth = AuthService.get_instance()
    
    # Register user
    auth.create_user("faculty_user", "password123", role="Faculty")
    
    # Login success
    logged_in = controller.login("faculty_user", "password123")
    assert logged_in is not None
    assert logged_in.username == "faculty_user"
    assert logged_in.role == "Faculty"
    
    # Login failure - wrong password
    bad_pass = controller.login("faculty_user", "wrong_password")
    assert bad_pass is None
    
    # Login failure - non-existent user
    bad_user = controller.login("non_existent", "password123")
    assert bad_user is None

def test_face_detector_singleton_reuse() -> None:
    """
    Verifies that FaceDetectorService implements a singleton pattern and does not recreate instances.
    """
    # Force reset instance for test reliability
    FaceDetectorService._instance = None
    
    # Fetch two instances
    detector1 = FaceDetectorService.get_instance(min_face_size=80)
    detector2 = FaceDetectorService.get_instance(min_face_size=80)
    
    # Both references should point to the exact same memory object
    assert detector1 is detector2
    assert detector2.min_face_size == 80

def test_dynamic_log_file_loading(tmp_path) -> None:
    """
    Validates the log file reading fallbacks.
    """
    log_file = tmp_path / "app_system.log"
    
    # File not found state
    assert log_file.exists() is False
    
    # Create log file and populate lines
    lines = [f"2026-08-17 Log line {i}\n" for i in range(100)]
    log_file.write_text("".join(lines), encoding="utf-8")
    assert log_file.exists() is True
    
    # Read last 35 lines
    with open(log_file, "r", encoding="utf-8") as f:
        read_lines = f.readlines()
        content = "".join(read_lines[-35:])
        
    assert len(content.strip().split("\n")) == 35
    assert "Log line 99" in content
    assert "Log line 65" in content
    assert "Log line 64" not in content

