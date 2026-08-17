# ==============================================================================
# Face Recognition Attendance System - Attendance Tracking Unit Tests
# ==============================================================================

import pytest
from datetime import datetime, timedelta
from src.core.database import initialize_database, get_session
from src.core.models import Student, Department, Course, Attendance, AttendanceSession
from src.services.student_service import StudentService
from src.services.attendance_service import AttendanceService, AttendanceResult
from src.utils.time_helper import get_current_date, get_current_time, get_local_now

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
        session.query(Attendance).delete()
        session.query(AttendanceSession).delete()
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
        "last_name": f"User-{code}",
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

# 1. Test successful check-in
def test_successful_check_in() -> None:
    student = create_test_student("STU001", "stu001@example.com")
    service = AttendanceService.get_instance()
    
    # Force clear cooldowns
    service.cooldown_cache.clear()
    
    result = service.mark_attendance(
        student_id=student.id,
        score=0.85,
        method="LBPH"
    )
    
    assert result.success is True
    assert result.student_id == student.id
    assert result.already_marked is False
    assert result.status in ("PRESENT", "LATE")
    
    # Query database to confirm
    session = get_session()
    record = session.query(Attendance).filter(Attendance.student_id == student.id).first()
    assert record is not None
    assert record.recognition_score == 0.85
    assert record.source == "FACE_RECOGNITION"
    session.close()

# 2. Test duplicate check-in prevention within the same day/session
def test_duplicate_check_in_prevention() -> None:
    student = create_test_student("STU002", "stu002@example.com")
    service = AttendanceService.get_instance()
    
    service.cooldown_cache.clear()
    
    # First marking
    res1 = service.mark_attendance(student.id, score=0.88)
    assert res1.success is True
    assert res1.already_marked is False
    
    # Second marking immediately (triggers cooldown cache match)
    res2 = service.mark_attendance(student.id, score=0.90)
    assert res2.success is True
    assert res2.already_marked is True
    assert res2.attendance_id is None  # Handled by cooldown bypass
    
    # Clear cooldown cache to check DB-level unique constraint handling
    service.cooldown_cache.clear()
    res3 = service.mark_attendance(student.id, score=0.91)
    assert res3.success is True
    assert res3.already_marked is True
    assert res3.attendance_id == res1.attendance_id  # Matches database PK

# 3. Test recognition cooldown window
def test_cooldown_cache_window() -> None:
    student = create_test_student("STU003", "stu003@example.com")
    service = AttendanceService.get_instance()
    
    service.cooldown_cache.clear()
    
    res1 = service.mark_attendance(student.id, score=0.82)
    assert res1.success is True
    assert service.is_in_cooldown(student.id) is True
    
    # Simulate time forward past cooldown (e.g. set last check-in to 31 minutes ago)
    service.cooldown_cache[student.id] = get_local_now() - timedelta(minutes=service.settings.cooldown_minutes + 1)
    assert service.is_in_cooldown(student.id) is False

# 4. Test manual attendance logging
def test_manual_attendance_marking() -> None:
    student = create_test_student("STU004", "stu004@example.com")
    service = AttendanceService.get_instance()
    
    res = service.mark_attendance(
        student_id=student.id,
        source="MANUAL",
        status="EXCUSED",
        date="2026-08-16",
        time_in="10:30:00",
        marked_by="Supervisor Override"
    )
    
    assert res.success is True
    assert res.already_marked is False
    assert res.status == "EXCUSED"
    
    # Verify in DB
    session = get_session()
    record = session.query(Attendance).filter(Attendance.student_id == student.id).first()
    assert record is not None
    assert record.source == "MANUAL"
    assert record.status == "EXCUSED"
    assert record.updated_by == "Supervisor Override"
    session.close()

# 5. Test attendance correction status update
def test_attendance_status_correction() -> None:
    student = create_test_student("STU005", "stu005@example.com")
    service = AttendanceService.get_instance()
    
    service.cooldown_cache.clear()
    res = service.mark_attendance(student.id, status="PRESENT")
    assert res.success is True
    
    # Correct it to LATE
    success, msg = service.update_attendance(
        record_id=res.attendance_id,
        status="LATE",
        updated_by="Registrar Correction"
    )
    assert success is True
    
    session = get_session()
    record = session.query(Attendance).filter(Attendance.id == res.attendance_id).first()
    assert record.status == "LATE"
    assert record.updated_by == "Registrar Correction"
    session.close()

# 6. Test statistics and filters list query
def test_statistics_and_query_filters() -> None:
    s1 = create_test_student("STU006", "stu006@example.com")
    s2 = create_test_student("STU007", "stu007@example.com")
    
    service = AttendanceService.get_instance()
    service.cooldown_cache.clear()
    
    # Log s1 as PRESENT, s2 as LATE
    service.mark_attendance(s1.id, status="PRESENT", date="2026-08-16")
    service.mark_attendance(s2.id, status="LATE", date="2026-08-16")
    
    # Check statistics
    stats = service.repo.get_today_statistics("2026-08-16")
    assert stats["total_marked"] == 2
    assert stats["present"] == 1
    assert stats["late"] == 1
    
    # Verify filter lists
    records = service.list_attendance(date_str="2026-08-16", status="LATE")
    assert len(records) == 1
    assert records[0].student_id == s2.id

# 7. Test unknown face / unregistered student ID
def test_unregistered_student_id() -> None:
    service = AttendanceService.get_instance()
    result = service.mark_attendance(student_id=99999, score=0.95)
    assert result.success is False
    assert "not found" in result.message.lower()

# 8. Test cooldown 10 minutes later (still blocked)
def test_cooldown_ten_minutes_later() -> None:
    student = create_test_student("STU010", "stu010@example.com")
    service = AttendanceService.get_instance()
    service.cooldown_cache.clear()
    
    # First check-in
    res1 = service.mark_attendance(student.id, score=0.85)
    assert res1.success is True
    assert res1.already_marked is False
    
    # 10 minutes later (still inside the 30-minute cooldown window)
    service.cooldown_cache[student.id] = get_local_now() - timedelta(minutes=10)
    res2 = service.mark_attendance(student.id, score=0.87)
    assert res2.success is True
    assert res2.already_marked is True
    assert res2.attendance_id is None

# 9. Test manual check-in uniqueness constraint handling
def test_manual_overwrite_unique_constraint() -> None:
    student = create_test_student("STU011", "stu011@example.com")
    service = AttendanceService.get_instance()
    service.cooldown_cache.clear()
    
    # Create recognition check-in first
    res1 = service.mark_attendance(student.id, score=0.92)
    assert res1.success is True
    
    # Try manual check-in on the same date and session
    res2 = service.mark_attendance(
        student_id=student.id,
        source="MANUAL",
        status="LATE",
        date=res1.date,
        marked_by="Admin"
    )
    
    # It should not crash or duplicate, but instead return success=True with already_marked=True
    assert res2.success is True
    assert res2.already_marked is True
    assert res2.attendance_id == res1.attendance_id

# 10. Test multiple recognized faces processing
def test_multiple_recognized_faces() -> None:
    s1 = create_test_student("STU012", "stu012@example.com")
    s2 = create_test_student("STU013", "stu013@example.com")
    service = AttendanceService.get_instance()
    service.cooldown_cache.clear()
    
    # Process both independently (simulates what GUI does in a loop over results list)
    res1 = service.mark_attendance(s1.id, score=0.91)
    res2 = service.mark_attendance(s2.id, score=0.88)
    
    assert res1.success is True and res1.already_marked is False
    assert res2.success is True and res2.already_marked is False

# 11. Test database transaction failure safety
def test_transaction_rollback_on_failure() -> None:
    student = create_test_student("STU014", "stu014@example.com")
    service = AttendanceService.get_instance()
    service.cooldown_cache.clear()
    
    # Mock create_record in repository to raise an exception
    from unittest.mock import patch
    with patch.object(service.repo, "create_record", side_effect=Exception("Database connection timed out")):
        res = service.mark_attendance(student.id, score=0.90)
        assert res.success is False
        assert "transaction failed" in res.message.lower()
        
        # Verify no record was created in the database
        session = get_session()
        record = session.query(Attendance).filter(Attendance.student_id == student.id).first()
        assert record is None
        session.close()

