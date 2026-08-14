# ==============================================================================
# Face Recognition Attendance System - Student Service
# ==============================================================================

import re
from datetime import datetime
from src.repositories.student_repository import StudentRepository
from src.core.database import get_session
from src.core.models import Department, Course

class StudentService:
    """
    Implements business validation checks and manages workflow rules 
    for student profile creations, updates, and listings.
    """
    
    def __init__(self) -> None:
        self.repo = StudentRepository()

    def get_student_by_id(self, student_id: int):
        """
        Retrieves a student by internal database surrogate key.
        """
        return self.repo.get_by_id(student_id)

    def list_students(self, **filters):
        """
        Retrieves filterable list of registered students.
        """
        return self.repo.list_students(**filters)

    def get_departments(self) -> list:
        """
        Returns all registered departments in the system.
        """
        with get_session() as session:
            return session.query(Department).all()

    def get_courses(self, department_id: int = None) -> list:
        """
        Returns all courses, optionally filtered by department ID.
        """
        with get_session() as session:
            query = session.query(Course)
            if department_id:
                query = query.filter(Course.department_id == department_id)
            return query.all()

    def get_statistics(self) -> dict:
        """
        Fetches student demographics dashboard counts.
        """
        return self.repo.get_statistics()

    def delete_student(self, student_id: int) -> bool:
        """
        Executes standard cascade delete.
        """
        return self.repo.delete(student_id)

    def save_student(self, student_data: dict, is_edit: bool = False, student_id: int = None) -> tuple[bool, str]:
        """
        Validates details and saves the student profile.
        Returns a tuple (success: bool, message: str).
        """
        # 1. Validation: Required fields check
        required_fields = [
            ("student_code", "Student ID"),
            ("first_name", "First Name"),
            ("last_name", "Last Name"),
            ("email", "Email"),
            ("phone", "Phone Number"),
            ("date_of_birth", "Date of Birth"),
            ("gender", "Gender"),
            ("department_id", "Department"),
            ("course_id", "Course"),
            ("year", "Year"),
            ("semester", "Semester"),
            ("enrollment_date", "Enrollment Date")
        ]
        
        for key, name in required_fields:
            val = student_data.get(key)
            if val is None or (isinstance(val, str) and not val.strip()):
                return False, f"Field '{name}' is required."

        # Clean string inputs
        student_code = student_data["student_code"].strip().upper()
        
        roll_val = student_data.get("roll_number", "")
        if roll_val is None:
            roll_val = ""
        roll_number = roll_val.strip().upper() or None
        email = student_data["email"].strip().lower()
        phone = student_data["phone"].strip()
        dob = student_data["date_of_birth"].strip()
        enroll_date = student_data["enrollment_date"].strip()

        # Update cleaned fields
        student_data["student_code"] = student_code
        student_data["roll_number"] = roll_number
        student_data["email"] = email
        student_data["phone"] = phone

        # 2. Validation: Uniqueness Checks
        # Uniqueness of Student Code
        existing_code = self.repo.get_by_code(student_code)
        if existing_code:
            if not is_edit or (is_edit and existing_code.id != student_id):
                return False, f"Student ID '{student_code}' is already registered."

        # Uniqueness of Roll Number (if set)
        if roll_number:
            existing_roll = self.repo.get_by_roll_number(roll_number)
            if existing_roll:
                if not is_edit or (is_edit and existing_roll.id != student_id):
                    return False, f"Roll Number '{roll_number}' is already assigned."

        # 3. Validation: Format Checks
        # Email format
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, email):
            return False, "Invalid email format."

        # Phone format
        phone_regex = r"^\+?[0-9\s-]{7,20}$"
        if not re.match(phone_regex, phone):
            return False, "Invalid phone number format."

        # Date of Birth format
        try:
            parsed_dob = datetime.strptime(dob, "%Y-%m-%d")
            if parsed_dob > datetime.now():
                return False, "Date of birth cannot be in the future."
        except ValueError:
            return False, "Date of Birth must be in YYYY-MM-DD format."

        # Enrollment Date format
        try:
            datetime.strptime(enroll_date, "%Y-%m-%d")
        except ValueError:
            return False, "Enrollment Date must be in YYYY-MM-DD format."

        # Academic numbers bounds check
        try:
            year = int(student_data["year"])
            sem = int(student_data["semester"])
            if year < 1 or year > 4:
                return False, "Academic Year must be between 1 and 4."
            if sem < 1 or sem > 8:
                return False, "Semester must be between 1 and 8."
        except ValueError:
            return False, "Year and Semester must be valid integers."

        # Status validation
        status = student_data.get("status", "Active")
        valid_statuses = ["Active", "Inactive", "Graduated", "Suspended"]
        if status not in valid_statuses:
            return False, f"Invalid Status. Must be one of: {', '.join(valid_statuses)}"

        # Save to database
        try:
            if is_edit:
                if not student_id:
                    return False, "Missing Student ID key context for updates."
                self.repo.update(student_id, student_data)
                return True, "Student updated successfully."
            else:
                self.repo.create(student_data)
                return True, "Student registered successfully."
        except Exception as e:
            return False, f"Database transaction failed: {str(e)}"
