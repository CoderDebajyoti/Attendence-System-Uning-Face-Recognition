# ==============================================================================
# Face Recognition Attendance System - Face Recognition Engine Unit Tests
# ==============================================================================

import pytest
import os
import shutil
import json
import numpy as np
import cv2
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.core.database import initialize_database, get_session
from src.core.models import Student, Department, Course, FaceDataset, DatasetImage
from src.services.student_service import StudentService
from src.services.dataset_service import DatasetService
from src.services.face_recognition_service import FaceRecognitionService
from src.controllers.recognition_controller import RecognitionController
from src.gui.pages.dataset import CameraReader

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

def create_test_student(code: str = "STD999", email: str = "test@example.com") -> Student:
    """
    Helper to onboard a standard student profile.
    """
    service = StudentService()
    dept_id, course_id = get_academic_ids()
    student_data = {
        "student_code": code,
        "roll_number": f"ROLL-{code}",
        "first_name": "Test",
        "last_name": "User",
        "email": email,
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
    student = session.query(Student).filter(Student.student_code == code).first()
    session.expunge(student)
    session.close()
    return student

# 1. Face Preprocessing Test
def test_face_preprocessing() -> None:
    service = FaceRecognitionService.get_instance()
    
    # Create dummy BGR image
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Bounding box
    box = (50, 50, 200, 200)
    
    gray_face = service.preprocess_face(dummy_frame, box)
    
    assert gray_face is not None
    assert len(gray_face.shape) == 2  # Grayscale
    assert gray_face.shape == (112, 112)  # Correct target size

# 2. Model Index Creation & Loading Tests
@patch("src.services.image_processing_service.ImageProcessingService.save_image", return_value=True)
def test_model_build_and_load(mock_save_image, tmp_path) -> None:
    student1 = create_test_student("STU001", "stu1@example.com")
    student2 = create_test_student("STU002", "stu2@example.com")
    
    # Create FaceDataset entries
    dataset_service = DatasetService()
    ds1 = dataset_service.get_or_create_dataset(student1.id)
    ds2 = dataset_service.get_or_create_dataset(student2.id)
    
    # Create fake files on disk and save DatasetImages
    session = get_session()
    
    # Generate mock images
    dummy_face = np.zeros((112, 112, 3), dtype=np.uint8)
    
    # Add target_image_count images to both datasets
    for i in range(25):
        img1_path = tmp_path / f"stu1_{i}.jpg"
        img2_path = tmp_path / f"stu2_{i}.jpg"
        
        cv2.imwrite(str(img1_path), dummy_face)
        cv2.imwrite(str(img2_path), dummy_face)
        
        img1 = DatasetImage(dataset_id=ds1.id, file_path=str(img1_path))
        img2 = DatasetImage(dataset_id=ds2.id, file_path=str(img2_path))
        session.add_all([img1, img2])
        
    session.commit()
    
    # Update dataset status to READY
    ds1_db = session.query(FaceDataset).filter(FaceDataset.id == ds1.id).first()
    ds2_db = session.query(FaceDataset).filter(FaceDataset.id == ds2.id).first()
    ds1_db.status = "READY"
    ds1_db.image_count = 25
    ds2_db.status = "READY"
    ds2_db.image_count = 25
    
    student1_db = session.query(Student).filter(Student.id == student1.id).first()
    student2_db = session.query(Student).filter(Student.id == student2.id).first()
    student1_db.face_dataset_status = "READY"
    student2_db.face_dataset_status = "READY"
    
    session.commit()
    session.close()
    
    # Configure custom model path
    model_dir = tmp_path / "models"
    settings_mock = MagicMock()
    settings_mock.model_path = model_dir
    settings_mock.target_image_count = 25
    settings_mock.recognition_threshold = 0.65
    
    # Clear singleton instance for test isolation
    FaceRecognitionService._instance = None
    rec_service = FaceRecognitionService.get_instance(settings_mock)
    
    # Verify initial state: not built
    assert rec_service.get_model_status() == "NOT_BUILT"
    
    # Build model
    report = rec_service.build_model()
    assert report["success"] is True
    assert report["students_included"] == 2
    assert report["images_included"] == 50
    
    # Verify files created
    assert (model_dir / "recognition_model.xml").exists()
    assert (model_dir / "recognition_model_metadata.json").exists()
    
    # Verify loaded state
    assert rec_service.model_loaded is True
    assert rec_service.get_model_status() == "READY"
    
    # Verify is_student_in_model
    assert rec_service.is_student_in_model(student1.id) is True
    assert rec_service.is_student_in_model(student2.id) is True
    assert rec_service.is_student_in_model(9999) is False

# 3. Validation and Outdated Status Tests
@patch("src.services.image_processing_service.ImageProcessingService.save_image", return_value=True)
def test_model_outdated_trigger(mock_save_image, tmp_path) -> None:
    student = create_test_student("STU003", "stu3@example.com")
    dataset_service = DatasetService()
    ds = dataset_service.get_or_create_dataset(student.id)
    
    session = get_session()
    dummy_face = np.zeros((112, 112, 3), dtype=np.uint8)
    for i in range(25):
        img_path = tmp_path / f"stu3_{i}.jpg"
        cv2.imwrite(str(img_path), dummy_face)
        img = DatasetImage(dataset_id=ds.id, file_path=str(img_path))
        session.add(img)
    session.commit()
    
    ds_db = session.query(FaceDataset).filter(FaceDataset.id == ds.id).first()
    ds_db.status = "READY"
    ds_db.image_count = 25
    student_db = session.query(Student).filter(Student.id == student.id).first()
    student_db.face_dataset_status = "READY"
    session.commit()
    session.close()
    
    model_dir = tmp_path / "models"
    settings_mock = MagicMock()
    settings_mock.model_path = model_dir
    settings_mock.target_image_count = 25
    settings_mock.recognition_threshold = 0.65
    
    FaceRecognitionService._instance = None
    rec_service = FaceRecognitionService.get_instance(settings_mock)
    
    # Train
    report = rec_service.build_model()
    assert report["success"] is True
    assert rec_service.get_model_status() == "READY"
    
    # Backdate the model's updated_at metadata, making the database's READY dataset newer
    rec_service.metadata["updated_at"] = (datetime.utcnow() - timedelta(minutes=10)).isoformat()
    with open(rec_service.metadata_file, "w", encoding="utf-8") as f:
        json.dump(rec_service.metadata, f)
    
    # Check status - should be OUTDATED because dataset was updated after the model's backdated timestamp
    assert rec_service.get_model_status() == "OUTDATED"
    
    # Rebuild
    report = rec_service.build_model()
    assert report["success"] is True
    assert rec_service.get_model_status() == "READY"

# 4. Dataset Filtering Test
@patch("src.services.image_processing_service.ImageProcessingService.save_image", return_value=True)
def test_dataset_filtering_during_training(mock_save_image, tmp_path) -> None:
    student1 = create_test_student("STU004", "stu4@example.com")
    student2 = create_test_student("STU005", "stu5@example.com")
    
    dataset_service = DatasetService()
    ds1 = dataset_service.get_or_create_dataset(student1.id)
    ds2 = dataset_service.get_or_create_dataset(student2.id)
    
    session = get_session()
    dummy_face = np.zeros((112, 112, 3), dtype=np.uint8)
    for i in range(25):
        img1_path = tmp_path / f"stu4_{i}.jpg"
        img2_path = tmp_path / f"stu5_{i}.jpg"
        cv2.imwrite(str(img1_path), dummy_face)
        cv2.imwrite(str(img2_path), dummy_face)
        img1 = DatasetImage(dataset_id=ds1.id, file_path=str(img1_path))
        img2 = DatasetImage(dataset_id=ds2.id, file_path=str(img2_path))
        session.add_all([img1, img2])
    session.commit()
    
    ds1_db = session.query(FaceDataset).filter(FaceDataset.id == ds1.id).first()
    ds2_db = session.query(FaceDataset).filter(FaceDataset.id == ds2.id).first()
    
    # ds1 is READY
    ds1_db.status = "READY"
    ds1_db.image_count = 25
    # ds2 is COLLECTING (not ready)
    ds2_db.status = "COLLECTING"
    ds2_db.image_count = 25
    
    student1_db = session.query(Student).filter(Student.id == student1.id).first()
    student2_db = session.query(Student).filter(Student.id == student2.id).first()
    student1_db.face_dataset_status = "READY"
    student2_db.face_dataset_status = "COLLECTING"
    session.commit()
    session.close()
    
    model_dir = tmp_path / "models"
    settings_mock = MagicMock()
    settings_mock.model_path = model_dir
    settings_mock.target_image_count = 25
    settings_mock.recognition_threshold = 0.65
    
    FaceRecognitionService._instance = None
    rec_service = FaceRecognitionService.get_instance(settings_mock)
    
    report = rec_service.build_model()
    assert report["success"] is True
    assert report["students_included"] == 1  # Only student1
    assert report["students_skipped"] == 1   # student2 skipped

# 5. Matching, Thresholding, and Unknown Face Handling Tests
@patch("src.services.image_processing_service.ImageProcessingService.save_image", return_value=True)
def test_matching_thresholds_and_unknowns(mock_save_image, tmp_path) -> None:
    student = create_test_student("STU006", "stu6@example.com")
    dataset_service = DatasetService()
    ds = dataset_service.get_or_create_dataset(student.id)
    
    session = get_session()
    dummy_face = np.zeros((112, 112, 3), dtype=np.uint8)
    for i in range(25):
        img_path = tmp_path / f"stu6_{i}.jpg"
        cv2.imwrite(str(img_path), dummy_face)
        img = DatasetImage(dataset_id=ds.id, file_path=str(img_path))
        session.add(img)
    session.commit()
    
    ds_db = session.query(FaceDataset).filter(FaceDataset.id == ds.id).first()
    ds_db.status = "READY"
    ds_db.image_count = 25
    student_db = session.query(Student).filter(Student.id == student.id).first()
    student_db.face_dataset_status = "READY"
    session.commit()
    session.close()
    
    model_dir = tmp_path / "models"
    settings_mock = MagicMock()
    settings_mock.model_path = model_dir
    settings_mock.target_image_count = 25
    settings_mock.recognition_threshold = 0.65
    
    # We patch LBPHFaceRecognizer_create so we can mock the predict method
    mock_rec = MagicMock()
    mock_rec.predict.return_value = (student.id, 10.0) # perfect match
    
    with patch("cv2.face.LBPHFaceRecognizer_create", return_value=mock_rec):
        FaceRecognitionService._instance = None
        rec_service = FaceRecognitionService.get_instance(settings_mock)
        rec_service.build_model()
        
        # Test perfect match (above threshold 0.65)
        res = rec_service.recognize_frame(np.zeros((480, 640, 3), dtype=np.uint8), [(50, 50, 100, 100)])
        assert len(res) == 1
        assert res[0]["recognized"] is True
        assert res[0]["student_id"] == student.id
        assert res[0]["student_code"] == "STU006"
        assert res[0]["distance_or_similarity"] == 0.90
        
        # Test poor match (dist = 60 -> similarity = 0.40, which is below 0.65)
        mock_rec.predict.return_value = (student.id, 60.0)
        res2 = rec_service.recognize_frame(np.zeros((480, 640, 3), dtype=np.uint8), [(50, 50, 100, 100)])
        assert len(res2) == 1
        assert res2[0]["recognized"] is False
        assert res2[0]["student_id"] is None
        assert res2[0]["student_code"] == "UNKNOWN"
        
        # Test unrecognized label ID
        mock_rec.predict.return_value = (9999, 10.0)
        res3 = rec_service.recognize_frame(np.zeros((480, 640, 3), dtype=np.uint8), [(50, 50, 100, 100)])
        assert len(res3) == 1
        assert res3[0]["recognized"] is False

# 6. Multiple Faces Test
def test_multiple_face_handling() -> None:
    mock_rec = MagicMock()
    mock_rec.predict.return_value = (1, 50.0) # similarity = 0.50
    
    with patch("cv2.face.LBPHFaceRecognizer_create", return_value=mock_rec):
        FaceRecognitionService._instance = None
        rec_service = FaceRecognitionService.get_instance()
        rec_service.model_loaded = True
        rec_service.metadata = {"trained_student_ids": []}
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        boxes = [(10, 10, 50, 50), (100, 100, 60, 60)]
        
        results = rec_service.recognize_frame(frame, boxes, threshold=0.40)
        
        assert len(results) == 2
        assert results[0]["recognized"] is False
        assert results[1]["recognized"] is False
        assert results[0]["bounding_box"] == boxes[0]
        assert results[1]["bounding_box"] == boxes[1]

# 7. Invalid Model Handling Test
def test_invalid_model_handling(tmp_path) -> None:
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    
    # Create empty/corrupt model files
    model_file = model_dir / "recognition_model.xml"
    metadata_file = model_dir / "recognition_model_metadata.json"
    
    with open(model_file, "w") as f:
        f.write("corrupted data")
    with open(metadata_file, "w") as f:
        f.write("{invalid json")
        
    settings_mock = MagicMock()
    settings_mock.model_path = model_dir
    
    FaceRecognitionService._instance = None
    rec_service = FaceRecognitionService.get_instance(settings_mock)
    
    assert rec_service.model_loaded is False
    assert rec_service.get_model_status() == "INVALID"

# 8. Camera Reader failure tests
def test_camera_reader_failure() -> None:
    # Mock cv2.VideoCapture so that isOpened returns False immediately
    with patch("cv2.VideoCapture") as mock_cap_class:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_cap_class.return_value = mock_cap
        
        reader = CameraReader("rtsp://invalid_address:8554/live")
        
        reader.start()
        reader.join(timeout=2.0)
        
        assert reader.error_occurred is True
        assert "Camera unavailable" in reader.error_message
        assert reader.running is False
