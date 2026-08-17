# ==============================================================================
# Face Recognition Attendance System - Attendance Repository
# ==============================================================================

from src.core.database import get_session
from src.core.models import Attendance, AttendanceSession, Student, Department, Course
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, and_, func
import logging

logger = logging.getLogger("app.database")

class AttendanceRepository:
    """
    Handles data operations for Attendance records and AttendanceSession entities.
    """

    def create_session(self, session_data: dict) -> AttendanceSession:
        """
        Creates a new attendance tracking session.
        """
        with get_session() as session:
            db_session = AttendanceSession(
                name=session_data["name"],
                date=session_data["date"],
                start_time=session_data["start_time"],
                end_time=session_data["end_time"],
                status=session_data.get("status", "Active"),
                created_by=session_data.get("created_by")
            )
            session.add(db_session)
            session.commit()
            session.refresh(db_session)
            return db_session

    def get_session_by_id(self, session_id: int) -> AttendanceSession | None:
        """
        Retrieves a session by internal primary key.
        """
        with get_session() as session:
            return session.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()

    def get_active_session_by_date(self, date_str: str) -> AttendanceSession | None:
        """
        Retrieves an active attendance session for a specific date YYYY-MM-DD.
        """
        with get_session() as session:
            return session.query(AttendanceSession).filter(
                AttendanceSession.date == date_str,
                AttendanceSession.status == "Active"
            ).order_by(AttendanceSession.id.desc()).first()

    def list_sessions(self) -> list[AttendanceSession]:
        """
        Returns all sessions ordered by date desc, start_time desc.
        """
        with get_session() as session:
            return session.query(AttendanceSession).order_by(
                AttendanceSession.date.desc(),
                AttendanceSession.start_time.desc()
            ).all()

    def create_record(self, record_data: dict) -> Attendance:
        """
        Inserts a new attendance log record.
        """
        with get_session() as session:
            # Filter dict keys to match Attendance table columns
            safe_data = {k: v for k, v in record_data.items() if hasattr(Attendance, k)}
            record = Attendance(**safe_data)
            session.add(record)
            session.commit()
            session.refresh(record)
            # Access relationships to trigger loading before detach
            _ = record.student
            if record.session:
                _ = record.session
            return record

    def get_record_by_id(self, record_id: int) -> Attendance | None:
        """
        Retrieves a single attendance record with student relationships loaded.
        """
        with get_session() as session:
            return session.query(Attendance).options(
                joinedload(Attendance.student).joinedload(Student.department),
                joinedload(Attendance.student).joinedload(Student.course),
                joinedload(Attendance.session)
            ).filter(Attendance.id == record_id).first()

    def find_record(self, student_id: int, date_str: str, session_id: int | None = None) -> Attendance | None:
        """
        Checks if a record exists for a student in a specific session or date.
        """
        with get_session() as session:
            query = session.query(Attendance).filter(
                Attendance.student_id == student_id,
                Attendance.date == date_str
            )
            if session_id is not None:
                query = query.filter(Attendance.session_id == session_id)
            return query.first()

    def update_record(self, record_id: int, update_data: dict) -> Attendance:
        """
        Modifies status and metadata of an existing attendance record.
        """
        with get_session() as session:
            record = session.query(Attendance).filter(Attendance.id == record_id).first()
            if not record:
                raise ValueError(f"Attendance record with ID {record_id} not found.")

            for key, val in update_data.items():
                if hasattr(Attendance, key):
                    setattr(record, key, val)

            session.commit()
            session.refresh(record)
            _ = record.student
            if record.session:
                _ = record.session
            return record

    def delete_record(self, record_id: int) -> bool:
        """
        Deletes a single attendance record.
        """
        with get_session() as session:
            record = session.query(Attendance).filter(Attendance.id == record_id).first()
            if not record:
                return False
            session.delete(record)
            session.commit()
            return True

    def list_attendance(
        self,
        search_query: str | None = None,
        date_str: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        status: str | None = None,
        department_id: int | None = None,
        course_id: int | None = None,
        source: str | None = None,
        session_id: int | None = None
    ) -> list[Attendance]:
        """
        Lists attendance records based on filters. Supports date ranges and search.
        """
        with get_session() as session:
            query = session.query(Attendance).join(Attendance.student).options(
                joinedload(Attendance.student).joinedload(Student.department),
                joinedload(Attendance.student).joinedload(Student.course),
                joinedload(Attendance.session)
            )

            # Apply date filters
            if date_str:
                query = query.filter(Attendance.date == date_str)
            else:
                if start_date:
                    query = query.filter(Attendance.date >= start_date)
                if end_date:
                    query = query.filter(Attendance.date <= end_date)

            # Apply categorization filters
            if status:
                query = query.filter(Attendance.status == status)
            if source:
                query = query.filter(Attendance.source == source)
            if session_id is not None:
                query = query.filter(Attendance.session_id == session_id)
            if department_id:
                query = query.filter(Student.department_id == department_id)
            if course_id:
                query = query.filter(Student.course_id == course_id)

            # Apply search criteria
            if search_query:
                q = f"%{search_query}%"
                query = query.filter(
                    or_(
                        Student.student_code.like(q),
                        Student.first_name.like(q),
                        Student.last_name.like(q),
                        Student.roll_number.like(q)
                    )
                )

            return query.order_by(Attendance.date.desc(), Attendance.time_in.desc()).all()

    def get_student_attendance_summary(self, student_id: int) -> dict:
        """
        Returns stats for a specific student: Total, Present, Late, Absent, Attendance Rate.
        """
        with get_session() as session:
            total_records = session.query(Attendance).filter(Attendance.student_id == student_id).count()
            present = session.query(Attendance).filter(
                Attendance.student_id == student_id,
                Attendance.status == "PRESENT"
            ).count()
            late = session.query(Attendance).filter(
                Attendance.student_id == student_id,
                Attendance.status == "LATE"
            ).count()
            absent = session.query(Attendance).filter(
                Attendance.student_id == student_id,
                Attendance.status == "ABSENT"
            ).count()
            excused = session.query(Attendance).filter(
                Attendance.student_id == student_id,
                Attendance.status == "EXCUSED"
            ).count()

            # Calculate rate based on Present + Late out of Total
            total_marked = present + late + absent + excused
            rate = 0.0
            if total_marked > 0:
                rate = ((present + late) / total_marked) * 100.0

            return {
                "total": total_marked,
                "present": present,
                "late": late,
                "absent": absent,
                "excused": excused,
                "rate": round(rate, 2)
            }

    def get_recent_student_records(self, student_id: int, limit: int = 5) -> list[Attendance]:
        """
        Returns recent logs for a student.
        """
        with get_session() as session:
            return session.query(Attendance).options(
                joinedload(Attendance.session)
            ).filter(
                Attendance.student_id == student_id
            ).order_by(
                Attendance.date.desc(),
                Attendance.time_in.desc()
            ).limit(limit).all()

    def get_today_statistics(self, date_str: str, session_id: int | None = None) -> dict:
        """
        Aggregates dashboard stats for today's attendance.
        """
        with get_session() as session:
            query = session.query(Attendance).filter(Attendance.date == date_str)
            if session_id is not None:
                query = query.filter(Attendance.session_id == session_id)

            total_marked = query.count()
            present = query.filter(Attendance.status == "PRESENT").count()
            late = query.filter(Attendance.status == "LATE").count()
            absent = query.filter(Attendance.status == "ABSENT").count()
            excused = query.filter(Attendance.status == "EXCUSED").count()

            # Total registered students
            total_students = session.query(Student).filter(Student.is_active == True, Student.status == "Active").count()
            
            rate = 0.0
            if total_students > 0:
                rate = ((present + late) / total_students) * 100.0

            return {
                "total_marked": total_marked,
                "present": present,
                "late": late,
                "absent": absent,
                "excused": excused,
                "total_students": total_students,
                "rate": round(rate, 2)
            }
