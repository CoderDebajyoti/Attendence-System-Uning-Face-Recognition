# ==============================================================================
# Face Recognition Attendance System - Reports & Analytics Unit Tests
# ==============================================================================

import pytest
import os
from pathlib import Path
from datetime import datetime, timedelta
from src.core.database import initialize_database, get_session
from src.core.models import Student, Department, Course, Attendance, AttendanceSession
from src.services.student_service import StudentService
from src.services.attendance_service import AttendanceService
from src.services.attendance_analytics_service import AttendanceAnalyticsService
from src.services.attendance_report_service import AttendanceReportService
from src.utils.time_helper import get_current_date, get_local_now

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

# 1. Test Date Range Validation
def test_validate_date_range() -> None:
    service = AttendanceReportService.get_instance()
    
    # Valid range
    valid, msg = service.validate_date_range("2026-08-01", "2026-08-15")
    assert valid is True
    
    # End before Start
    valid, msg = service.validate_date_range("2026-08-15", "2026-08-01")
    assert valid is False
    assert "cannot be after" in msg
    
    # Format error
    valid, msg = service.validate_date_range("08-15-2026", "2026-08-30")
    assert valid is False
    assert "format" in msg

# 2. Test Report Data Query and Filters
def test_generate_report_data() -> None:
    student1 = create_test_student("STU101", "stu101@example.com")
    student2 = create_test_student("STU102", "stu102@example.com")
    
    att_service = AttendanceService.get_instance()
    att_service.cooldown_cache.clear()
    
    # Check-in student 1 (Face Recognition)
    res1 = att_service.mark_attendance(student1.id, status="PRESENT", date="2026-08-10")
    assert res1.success is True
    
    # Check-in student 2 (Manual override)
    res2 = att_service.mark_attendance(
        student_id=student2.id,
        source="MANUAL",
        status="LATE",
        date="2026-08-11",
        marked_by="Admin"
    )
    assert res2.success is True
    
    report_service = AttendanceReportService.get_instance()
    
    # Filter: Date range
    report = report_service.generate_report_data("2026-08-01", "2026-08-15")
    assert len(report["records"]) == 2
    
    # Filter: Status
    report_status = report_service.generate_report_data("2026-08-01", "2026-08-15", status="LATE")
    assert len(report_status["records"]) == 1
    assert report_status["records"][0].student_id == student2.id
    
    # Filter: Source
    report_source = report_service.generate_report_data("2026-08-01", "2026-08-15", source="FACE_RECOGNITION")
    assert len(report_source["records"]) == 1
    assert report_source["records"][0].student_id == student1.id

# 3. Test Attendance Rate and Statistics
def test_attendance_rate_calculations() -> None:
    analytics = AttendanceAnalyticsService.get_instance()
    
    # Calculation checks
    assert analytics.calculate_attendance_rate(8, 2, 10) == 100.0  # (8+2)/10 * 100 = 100%
    assert analytics.calculate_attendance_rate(4, 1, 10) == 50.0   # (4+1)/10 * 100 = 50%
    assert analytics.calculate_attendance_rate(0, 0, 0) == 0.0

# 4. Test Student Detail Summary Analytics
def test_student_detail_analytics() -> None:
    student = create_test_student("STU103", "stu103@example.com")
    att_service = AttendanceService.get_instance()
    att_service.cooldown_cache.clear()
    
    # Check-ins
    att_service.mark_attendance(student.id, status="PRESENT", date="2026-08-10")
    att_service.cooldown_cache.clear()
    att_service.mark_attendance(student.id, status="LATE", date="2026-08-12")
    
    analytics = AttendanceAnalyticsService.get_instance()
    stats = analytics.get_student_statistics(student.id)

    
    assert stats["total_records"] == 2
    assert stats["present"] == 1
    assert stats["late"] == 1
    assert stats["rate"] == 100.0
    assert stats["first_attendance"] == "2026-08-10"
    assert stats["last_attendance"] == "2026-08-12"

# 5. Test CSV and Excel File Exporters
def test_csv_excel_exports(tmp_path) -> None:
    student = create_test_student("STU104", "stu104@example.com")
    att_service = AttendanceService.get_instance()
    att_service.cooldown_cache.clear()
    
    att_service.mark_attendance(student.id, status="PRESENT", date="2026-08-12")
    
    report_service = AttendanceReportService.get_instance()
    report_service.settings.export_path = tmp_path
    
    report_data = report_service.generate_report_data("2026-08-01", "2026-08-15")
    
    # Test CSV Export
    success_csv, msg_csv = report_service.export_to_csv(report_data)
    assert success_csv is True
    
    # Verify file exists
    csv_files = list(tmp_path.glob("*.csv"))
    assert len(csv_files) == 1
    
    # Test Excel Export
    success_excel, msg_excel = report_service.export_to_excel(report_data)
    assert success_excel is True
    
    # Verify file exists
    xlsx_files = list(tmp_path.glob("*.xlsx"))
    assert len(xlsx_files) == 1

# 6. Test Empty Reports Prevention
def test_empty_report_prevention() -> None:
    report_service = AttendanceReportService.get_instance()
    
    # Empty data
    empty_report_data = {
        "records": [],
        "summary": {},
        "start_date": "2026-08-01",
        "end_date": "2026-08-15"
    }
    
    success_csv, msg_csv = report_service.export_to_csv(empty_report_data)
    assert success_csv is False
    assert "no attendance records found" in msg_csv.lower()
