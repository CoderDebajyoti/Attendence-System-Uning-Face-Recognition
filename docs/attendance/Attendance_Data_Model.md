# Attendance Data Model

## Database Schemas

### AttendanceSession
```python
class AttendanceSession(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    date = Column(String(20), nullable=False)
    start_time = Column(String(20), nullable=False)
    end_time = Column(String(20), nullable=False)
    status = Column(String(20), default="Active", nullable=False)
    created_by = Column(String(100), nullable=True)
```

### Attendance
```python
class Attendance(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id"), nullable=True)
    subject_id = Column(Integer, nullable=True)
    date = Column(String(20), nullable=False)
    time_in = Column(String(20), nullable=False)
    time_out = Column(String(20), nullable=True)
    status = Column(String(20), nullable=False)  # PRESENT, LATE, ABSENT, EXCUSED
    recognition_score = Column(Float, nullable=True)
    recognition_method = Column(String(50), nullable=True)
    source = Column(String(20), nullable=False, default="FACE_RECOGNITION")
    updated_by = Column(String(100), nullable=True)
```

## Database Constraints

Duplicate logs protection is enforced at the database layer using a composite UniqueConstraint:
* `UniqueConstraint('student_id', 'date', 'session_id', name='uq_student_date_session')`
This guarantees data integrity even if service validation checks are bypassed.
