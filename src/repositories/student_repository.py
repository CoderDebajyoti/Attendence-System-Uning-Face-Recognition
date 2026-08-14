# ==============================================================================
# Face Recognition Attendance System - Student Repository
# ==============================================================================

from src.core.database import get_session
from src.core.models import Student, Department, Course
from sqlalchemy.orm import joinedload
from sqlalchemy import or_

class StudentRepository:
    """
    Handles standard data operations for Student records (CRUD, filtering, 
    statistics, and relationships query scopes).
    """
    
    def get_by_id(self, student_id: int) -> Student:
        """
        Retrieves a single student, eager loading department and course relations.
        """
        with get_session() as session:
            return session.query(Student).options(
                joinedload(Student.department),
                joinedload(Student.course)
            ).filter(Student.id == student_id).first()

    def get_by_code(self, student_code: str) -> Student:
        """
        Retrieves a student matching a student_code code tag.
        """
        with get_session() as session:
            return session.query(Student).filter(Student.student_code == student_code).first()

    def get_by_roll_number(self, roll_number: str) -> Student:
        """
        Retrieves a student matching a roll_number tag.
        """
        if not roll_number:
            return None
        with get_session() as session:
            return session.query(Student).filter(Student.roll_number == roll_number).first()

    def list_students(self, search_query=None, department_id=None, course_id=None, year=None, status=None, face_status=None):
        """
        Returns a list of students matching the given search and filter parameters.
        """
        with get_session() as session:
            query = session.query(Student).options(
                joinedload(Student.department),
                joinedload(Student.course)
            ).filter(Student.is_active == True)
            
            # Apply search queries across fields
            if search_query:
                q = f"%{search_query}%"
                query = query.filter(or_(
                    Student.student_code.like(q),
                    Student.first_name.like(q),
                    Student.last_name.like(q),
                    Student.email.like(q),
                    Student.roll_number.like(q)
                ))
                
            # Apply filter parameters
            if department_id:
                query = query.filter(Student.department_id == department_id)
            if course_id:
                query = query.filter(Student.course_id == course_id)
            if year:
                query = query.filter(Student.year == year)
            if status:
                query = query.filter(Student.status == status)
            if face_status:
                query = query.filter(Student.face_dataset_status == face_status)
                
            return query.order_by(Student.student_code).all()

    def create(self, student_data: dict) -> Student:
        """
        Saves a new student record to the database.
        """
        with get_session() as session:
            # Filter keys to match student table columns
            safe_data = {k: v for k, v in student_data.items() if hasattr(Student, k)}
            student = Student(**safe_data)
            session.add(student)
            session.commit()
            
            # Detach object from session transaction context after loading relations
            # Eager load relationships before query finishes to prevent lazy loading errors
            session.refresh(student)
            # Access attributes to trigger loading
            _ = student.department
            _ = student.course
            return student

    def update(self, student_id: int, student_data: dict) -> Student:
        """
        Updates database attributes of an existing student.
        """
        with get_session() as session:
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError(f"Student record with ID {student_id} not found.")
                
            for key, val in student_data.items():
                if hasattr(Student, key):
                    setattr(student, key, val)
                    
            session.commit()
            session.refresh(student)
            _ = student.department
            _ = student.course
            return student

    def delete(self, student_id: int) -> bool:
        """
        Deletes a student record (cascading deletes child embeddings/attendance records).
        """
        with get_session() as session:
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                return False
            session.delete(student)
            session.commit()
            return True

    def get_statistics(self) -> dict:
        """
        Returns count telemetry of active database student entries.
        """
        with get_session() as session:
            total = session.query(Student).filter(Student.is_active == True).count()
            active = session.query(Student).filter(Student.is_active == True, Student.status == "Active").count()
            inactive = session.query(Student).filter(Student.is_active == True, Student.status == "Inactive").count()
            with_dataset = session.query(Student).filter(Student.is_active == True, Student.face_dataset_status == "Ready").count()
            without_dataset = total - with_dataset
            
            return {
                "total": total,
                "active": active,
                "inactive": inactive,
                "with_dataset": with_dataset,
                "without_dataset": without_dataset
            }
