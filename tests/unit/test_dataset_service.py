# ==============================================================================
# Face Recognition Attendance System - Face Dataset Service Unit Tests
# ==============================================================================

import pytest
import os
import shutil
import numpy as np
import cv2
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.core.database import initialize_database, get_session
from src.core.models import Student, Department, Course, FaceDataset, DatasetImage
from src.services.student_service import StudentService
from src.services.dataset_service import DatasetService

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
        session.query(DatasetImage).delete()
        session.query(FaceDataset).delete()
        session.query(Student).delete()
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()

def get_academic_ids() -> tuple[int, int]:
    session = get_session()
    dept = session.query(Department).filter(Department.code == "CSE").first()
    course = session.query(Course).filter(Course.code == "BTECH-CSE").first()
    dept_id, course_id = dept.id, course.id
    session.close()
    return dept_id, course_id

def create_test_student() -> Student:
    """
    Helper to onboard a standard student profile.
    """
    service = StudentService()
    dept_id, course_id = get_academic_ids()
    student_data = {
        "student_code": "STD2026999",
        "roll_number": "CSE-26-999",
        "first_name": "Test",
        "last_name": "User",
        "email": "testuser@example.com",
        "phone": "+91 9999999999",
        "date_of_birth": "2000-01-01",
        "gender": "Male",
        "department_id": dept_id,
        "course_id": course_id,
        "year": 2,
        "semester": 3,
        "enrollment_date": "2026-08-01",
        "status": "Active"
    }
    success, _ = service.save_student(student_data)
    assert success is True
    
    session = get_session()
    student = session.query(Student).filter(Student.student_code == "STD2026999").first()
    # Detach
    session.expunge(student)
    session.close()
    return student

def test_dataset_initialization() -> None:
    """
    Tests that requesting a dataset lazy-initializes a FaceDataset database row.
    """
    student = create_test_student()
    service = DatasetService()
    
    # Verify dataset doesn't exist yet
    session = get_session()
    assert session.query(FaceDataset).filter(FaceDataset.student_id == student.id).first() is None
    session.close()

    # Get or create
    dataset = service.get_or_create_dataset(student.id)
    assert dataset is not None
    assert dataset.student_id == student.id
    assert dataset.status == "NOT_REGISTERED"
    assert dataset.image_count == 0
    assert "STD2026999" in dataset.dataset_path

    # Verify persisted in DB
    session = get_session()
    db_dataset = session.query(FaceDataset).filter(FaceDataset.student_id == student.id).first()
    assert db_dataset is not None
    assert db_dataset.status == "NOT_REGISTERED"
    session.close()

@patch("src.services.face_detector_service.FaceDetectorService.validate_face_for_dataset")
@patch("src.services.image_processing_service.ImageProcessingService.check_quality")
@patch("src.services.image_processing_service.ImageProcessingService.save_image")
def test_image_capture_success(mock_save_image, mock_check_quality, mock_validate_face) -> None:
    """
    Tests that a successful face capture crops, saves the file, updates status, and increments counter.
    """
    student = create_test_student()
    service = DatasetService()
    
    # Mock face validation success
    mock_validate_face.return_value = (True, "Face detected. Image captured.", [(50, 50, 150, 150)])
    # Mock image quality check success
    mock_check_quality.return_value = (True, "Quality check passed.")
    # Mock file saving success
    mock_save_image.return_value = True

    # Capture dummy frame (NumPy matrix representation)
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    success, msg, data = service.capture_image(student.id, dummy_frame)
    assert success is True
    assert "Image captured" in msg
    assert "file_path" in data
    assert data["filename"] == "image_001.jpg"

    # Verify status transitioned to COLLECTING and count is 1
    dataset = service.get_or_create_dataset(student.id)
    assert dataset.image_count == 1
    assert dataset.status == "COLLECTING"
    
    session = get_session()
    db_student = session.query(Student).filter(Student.id == student.id).first()
    assert db_student.face_dataset_status == "COLLECTING"
    session.close()

@patch("src.services.face_detector_service.FaceDetectorService.validate_face_for_dataset")
def test_image_capture_validation_failure(mock_validate_face) -> None:
    """
    Tests that an invalid face (e.g. no face or multiple faces) is rejected and not saved.
    """
    student = create_test_student()
    service = DatasetService()
    
    # Mock face validation failure (multiple faces)
    mock_validate_face.return_value = (False, "Multiple faces detected. Please ensure only one person is visible.", [])

    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    success, msg, data = service.capture_image(student.id, dummy_frame)
    assert success is False
    assert "Multiple faces" in msg
    assert data == {}

    # Verify dataset status is still NOT_REGISTERED
    dataset = service.get_or_create_dataset(student.id)
    assert dataset.image_count == 0
    assert dataset.status == "NOT_REGISTERED"

@patch("src.services.face_detector_service.FaceDetectorService.validate_face_for_dataset")
@patch("src.services.image_processing_service.ImageProcessingService.check_quality")
@patch("src.services.image_processing_service.ImageProcessingService.save_image")
def test_image_deletion_and_reset(mock_save_image, mock_check_quality, mock_validate_face) -> None:
    """
    Tests deleting an individual image and verifying image counts adjust.
    """
    student = create_test_student()
    service = DatasetService()
    
    mock_validate_face.return_value = (True, "Face detected. Image captured.", [(50, 50, 150, 150)])
    mock_check_quality.return_value = (True, "Quality check passed.")
    mock_save_image.return_value = True

    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    success, _, data = service.capture_image(student.id, dummy_frame)
    assert success is True
    image_id = data["id"]

    # Delete image
    with patch("os.remove") as mock_os_remove, patch("pathlib.Path.exists", return_value=True):
        deleted = service.delete_image(student.id, image_id)
        assert deleted is True
        mock_os_remove.assert_called_once()

    # Verify image count is 0 and status is NOT_REGISTERED
    dataset = service.get_or_create_dataset(student.id)
    assert dataset.image_count == 0
    assert dataset.status == "NOT_REGISTERED"

@patch("src.services.face_detector_service.FaceDetectorService.validate_face_for_dataset")
@patch("src.services.image_processing_service.ImageProcessingService.check_quality")
@patch("src.services.image_processing_service.ImageProcessingService.save_image")
def test_clear_entire_dataset(mock_save_image, mock_check_quality, mock_validate_face) -> None:
    """
    Tests clearing the entire student dataset and deleting files.
    """
    student = create_test_student()
    service = DatasetService()
    
    mock_validate_face.return_value = (True, "Face detected. Image captured.", [(50, 50, 150, 150)])
    mock_check_quality.return_value = (True, "Quality check passed.")
    mock_save_image.return_value = True

    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    service.capture_image(student.id, dummy_frame)
    service.capture_image(student.id, dummy_frame)

    dataset = service.get_or_create_dataset(student.id)
    assert dataset.image_count == 2

    # Clear dataset
    with patch("shutil.rmtree") as mock_rmtree:
        success = service.clear_dataset(student.id)
        assert success is True
        mock_rmtree.assert_called_once_with(Path(dataset.dataset_path))

    # Verify counters reset
    dataset_after = service.get_or_create_dataset(student.id)
    assert dataset_after.image_count == 0
    assert dataset_after.status == "NOT_REGISTERED"

@patch("src.services.face_detector_service.FaceDetectorService.validate_face_for_dataset")
@patch("src.services.image_processing_service.ImageProcessingService.check_quality")
@patch("src.services.image_processing_service.ImageProcessingService.save_image")
@patch("src.services.dataset_service.cv2.imread")
@patch("src.services.face_detector_service.FaceDetectorService.detect_faces")
def test_dataset_audit_validation_flow(mock_detect_faces, mock_imread, mock_save_image, mock_check_quality, mock_validate_face) -> None:
    """
    Tests the validation service checking counts, dimensions, readability, and face count.
    """
    student = create_test_student()
    service = DatasetService()
    service.settings.target_image_count = 5  # Reduce target for quick testing

    mock_validate_face.return_value = (True, "Face detected. Image captured.", [(50, 50, 150, 150)])
    mock_check_quality.return_value = (True, "Quality check passed.")
    mock_save_image.return_value = True

    valid_crop = np.zeros((112, 112, 3), dtype=np.uint8)
    mock_imread.return_value = valid_crop
    mock_detect_faces.return_value = [(10, 10, 92, 92)]  # Exactly one face
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # 1. Capture only 2 images (target is 5)
    service.capture_image(student.id, dummy_frame)
    service.capture_image(student.id, dummy_frame)

    # Run validation (should fail count check)
    with patch("pathlib.Path.exists", return_value=True):
        res = service.validate_dataset(student.id)
        assert res["success"] is False
        assert res["status"] == "NEEDS_UPDATE"
        assert "Insufficient images" in res["validation_result"]

    # 2. Capture remaining to hit target 5
    service.capture_image(student.id, dummy_frame)
    service.capture_image(student.id, dummy_frame)
    service.capture_image(student.id, dummy_frame)

    # Mock cv2 reads for validation checks
    valid_crop = np.zeros((112, 112, 3), dtype=np.uint8)
    mock_imread.return_value = valid_crop
    mock_detect_faces.return_value = [(10, 10, 92, 92)]  # Exactly one face

    with patch("pathlib.Path.exists", return_value=True):
        res = service.validate_dataset(student.id)
        assert res["success"] is True
        assert res["status"] == "READY"
        assert len(res["errors"]) == 0
        assert "All checks passed" in res["validation_result"]

    # Verify status synced to database Student
    session = get_session()
    db_student = session.query(Student).filter(Student.id == student.id).first()
    assert db_student.face_dataset_status == "READY"
    session.close()
