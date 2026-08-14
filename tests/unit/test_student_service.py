# ==============================================================================
# Face Recognition Attendance System - Student Service Unit Tests
# ==============================================================================

import pytest
from src.core.database import initialize_database, get_session
from src.core.models import Student, Department, Course
from src.services.student_service import StudentService

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
        session.query(Student).delete()
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()

def get_academic_ids() -> tuple[int, int]:
    """
    Helper to fetch seeded CSE IDs.
    """
    session = get_session()
    dept = session.query(Department).filter(Department.code == "CSE").first()
    course = session.query(Course).filter(Course.code == "BTECH-CSE").first()
    dept_id, course_id = dept.id, course.id
    session.close()
    return dept_id, course_id

def test_student_registration() -> None:
    service = StudentService()
    dept_id, course_id = get_academic_ids()

    student_data = {
        "student_code": "STD2026001",
        "roll_number": "CSE-26-001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "phone": "+91 9876543210",
        "date_of_birth": "2000-01-01",
        "gender": "Male",
        "address": "123 Main St",
        "department_id": dept_id,
        "course_id": course_id,
        "year": 2,
        "semester": 3,
        "enrollment_date": "2026-08-01",
        "status": "Active"
    }

    success, message = service.save_student(student_data)
    assert success is True
    assert message == "Student registered successfully."

    # Retrieve and check profile integrity
    students = service.list_students()
    assert len(students) == 1
    assert students[0].first_name == "John"
    assert students[0].last_name == "Doe"
    assert students[0].student_code == "STD2026001"
    assert students[0].department.code == "CSE"
    assert students[0].course.code == "BTECH-CSE"

def test_duplicate_student_code_collision() -> None:
    service = StudentService()
    dept_id, course_id = get_academic_ids()

    student1 = {
        "student_code": "STD2026001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "phone": "+91 9876543210",
        "date_of_birth": "2000-01-01",
        "gender": "Male",
        "department_id": dept_id,
        "course_id": course_id,
        "year": 2,
        "semester": 3,
        "enrollment_date": "2026-08-01",
    }
    success, _ = service.save_student(student1)
    assert success is True

    # Same Student Code, different email
    student2 = student1.copy()
    student2["email"] = "different@example.com"
    
    success, message = service.save_student(student2)
    assert success is False
    assert "already registered" in message

def test_duplicate_roll_number_collision() -> None:
    service = StudentService()
    dept_id, course_id = get_academic_ids()

    student1 = {
        "student_code": "STD2026001",
        "roll_number": "CSE-26-001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "phone": "+91 9876543210",
        "date_of_birth": "2000-01-01",
        "gender": "Male",
        "department_id": dept_id,
        "course_id": course_id,
        "year": 2,
        "semester": 3,
        "enrollment_date": "2026-08-01",
    }
    success, _ = service.save_student(student1)
    assert success is True

    # Different Code, same Roll Number
    student2 = student1.copy()
    student2["student_code"] = "STD2026002"
    student2["email"] = "other@example.com"
    
    success, message = service.save_student(student2)
    assert success is False
    assert "already assigned" in message

def test_format_validation_failures() -> None:
    service = StudentService()
    dept_id, course_id = get_academic_ids()

    base_profile = {
        "student_code": "STD2026001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "phone": "+91 9876543210",
        "date_of_birth": "2000-01-01",
        "gender": "Male",
        "department_id": dept_id,
        "course_id": course_id,
        "year": 2,
        "semester": 3,
        "enrollment_date": "2026-08-01",
    }

    # 1. Invalid email
    bad_email = base_profile.copy()
    bad_email["email"] = "invalid_email_format"
    success, msg = service.save_student(bad_email)
    assert success is False
    assert "Invalid email" in msg

    # 2. Invalid phone
    bad_phone = base_profile.copy()
    bad_phone["phone"] = "abc123phone"
    success, msg = service.save_student(bad_phone)
    assert success is False
    assert "Invalid phone" in msg

    # 3. Invalid DOB calendar date format
    bad_dob = base_profile.copy()
    bad_dob["date_of_birth"] = "2000/01/01"
    success, msg = service.save_student(bad_dob)
    assert success is False
    assert "format" in msg.lower()

    # 4. Out of bounds Year/Semester
    bad_year = base_profile.copy()
    bad_year["year"] = 5
    success, msg = service.save_student(bad_year)
    assert success is False
    assert "Year" in msg

def test_student_updates() -> None:
    service = StudentService()
    dept_id, course_id = get_academic_ids()

    student_data = {
        "student_code": "STD2026001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "phone": "+91 9876543210",
        "date_of_birth": "2000-01-01",
        "gender": "Male",
        "department_id": dept_id,
        "course_id": course_id,
        "year": 2,
        "semester": 3,
        "enrollment_date": "2026-08-01",
    }
    
    success, _ = service.save_student(student_data)
    assert success is True

    # Retrieve record ID context
    db_student = service.list_students()[0]
    student_id = db_student.id

    # Modify email and phone fields
    updated_data = student_data.copy()
    updated_data["email"] = "newemail@example.com"
    updated_data["phone"] = "+91 9999999999"

    success, msg = service.save_student(updated_data, is_edit=True, student_id=student_id)
    assert success is True
    
    modified_student = service.get_student_by_id(student_id)
    assert modified_student.email == "newemail@example.com"
    assert modified_student.phone == "+91 9999999999"

def test_student_deletion() -> None:
    service = StudentService()
    dept_id, course_id = get_academic_ids()

    student_data = {
        "student_code": "STD2026001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "phone": "+91 9876543210",
        "date_of_birth": "2000-01-01",
        "gender": "Male",
        "department_id": dept_id,
        "course_id": course_id,
        "year": 2,
        "semester": 3,
        "enrollment_date": "2026-08-01",
    }
    
    success, _ = service.save_student(student_data)
    assert success is True

    db_student = service.list_students()[0]
    student_id = db_student.id

    # Remove student
    deleted = service.delete_student(student_id)
    assert deleted is True
    assert len(service.list_students()) == 0

def test_dashboard_statistics() -> None:
    service = StudentService()
    dept_id, course_id = get_academic_ids()

    # Base counts empty checks
    stats = service.get_statistics()
    assert stats["total"] == 0

    student1 = {
        "student_code": "STD2026001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "phone": "+91 9876543210",
        "date_of_birth": "2000-01-01",
        "gender": "Male",
        "department_id": dept_id,
        "course_id": course_id,
        "year": 2,
        "semester": 3,
        "enrollment_date": "2026-08-01",
        "status": "Active"
    }
    service.save_student(student1)

    student2 = {
        "student_code": "STD2026002",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "janesmith@example.com",
        "phone": "+91 9876543211",
        "date_of_birth": "2001-02-02",
        "gender": "Female",
        "department_id": dept_id,
        "course_id": course_id,
        "year": 1,
        "semester": 1,
        "enrollment_date": "2026-08-01",
        "status": "Inactive"
    }
    service.save_student(student2)

    stats = service.get_statistics()
    assert stats["total"] == 2
    assert stats["active"] == 1
    assert stats["inactive"] == 1
