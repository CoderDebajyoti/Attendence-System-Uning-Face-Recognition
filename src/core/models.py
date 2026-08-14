# ==============================================================================
# Face Recognition Attendance System - Database Schema Models
# ==============================================================================

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Time, DateTime, Float, LargeBinary
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Department(Base):
    """
    Academic or organizational departments (e.g. CSE, ECE).
    """
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    
    courses = relationship("Course", back_populates="department", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="department")

class Course(Base):
    """
    Academic degree plans (e.g. BTECH-CSE, BTECH-ECE).
    """
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False)
    
    department = relationship("Department", back_populates="courses")
    students = relationship("Student", back_populates="course")

class Student(Base):
    """
    Student records biometrically tracked by the system.
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(50), unique=True, nullable=False)
    roll_number = Column(String(50), unique=True, nullable=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    date_of_birth = Column(String(20), nullable=False)  # YYYY-MM-DD
    gender = Column(String(10), nullable=False)
    address = Column(String(255), nullable=True)
    
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False)
    
    year = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    enrollment_date = Column(String(20), nullable=False)  # YYYY-MM-DD
    status = Column(String(20), default="Active", nullable=False)  # Active, Inactive, Graduated, Suspended
    face_dataset_status = Column(String(20), default="NOT_REGISTERED", nullable=False)  # NOT_REGISTERED, COLLECTING, READY, NEEDS_UPDATE, INVALID
    is_active = Column(Boolean, default=True, nullable=False)
    
    department = relationship("Department", back_populates="students")
    course = relationship("Course", back_populates="students")
    face_dataset = relationship("FaceDataset", back_populates="student", uselist=False, cascade="all, delete-orphan")
    face_embeddings = relationship("FaceEmbedding", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    attendance_logs = relationship("AttendanceLog", back_populates="student", cascade="all, delete-orphan")

class FaceDataset(Base):
    """
    Biometric face dataset registry containing session status and validation metadata.
    """
    __tablename__ = "face_datasets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False)
    dataset_path = Column(String(255), nullable=False)
    image_count = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default="NOT_REGISTERED", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_validation = Column(DateTime, nullable=True)
    validation_result = Column(String(500), nullable=True)

    student = relationship("Student", back_populates="face_dataset")
    images = relationship("DatasetImage", back_populates="face_dataset", cascade="all, delete-orphan")

class DatasetImage(Base):
    """
    Registry for individual processed face crops in a biometric dataset.
    """
    __tablename__ = "dataset_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("face_datasets.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    face_dataset = relationship("FaceDataset", back_populates="images")

class FaceEmbedding(Base):
    """
    Biometric face feature vector templates.
    """
    __tablename__ = "face_embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    embedding_blob = Column(LargeBinary, nullable=False)  # NumPy float512 array serialized
    file_path = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    student = relationship("Student", back_populates="face_embeddings")

class Attendance(Base):
    """
    Daily attendance logs registry.
    """
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, nullable=False)  # Decoupled standard key or ForeignKey
    date = Column(String(20), nullable=False)  # YYYY-MM-DD
    time_in = Column(String(20), nullable=False)  # HH:MM:SS
    status = Column(String(20), nullable=False)  # Present, Absent, Late, Excused
    marked_by_user_id = Column(Integer, nullable=True)
    
    student = relationship("Student", back_populates="attendance_records")

class AttendanceLog(Base):
    """
    Camera match score trace log history.
    """
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=True)
    similarity_score = Column(Float, nullable=False)
    matched_embedding_id = Column(Integer, ForeignKey("face_embeddings.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    image_path = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False)
    
    student = relationship("Student", back_populates="attendance_logs")
