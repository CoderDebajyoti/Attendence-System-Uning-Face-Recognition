# ==============================================================================
# Face Recognition Attendance System - Attendance Service
# ==============================================================================

import logging
from datetime import datetime, timedelta
from src.core.config import ConfigLoader
from src.core.database import get_session
from src.core.models import Student, AttendanceSession, Attendance
from src.repositories.attendance_repository import AttendanceRepository
from src.repositories.student_repository import StudentRepository
from src.utils.time_helper import get_utc_now, get_local_now, get_current_date, get_current_time

logger = logging.getLogger("app.attendance")

class AttendanceResult:
    """
    Structured response payload returning the results of a check-in attempt.
    """
    def __init__(
        self,
        success: bool,
        student_id: int | None,
        student_name: str,
        attendance_id: int | None,
        date: str,
        time: str,
        status: str,
        already_marked: bool,
        recognition_score: float | None,
        message: str
    ) -> None:
        self.success = success
        self.student_id = student_id
        self.student_name = student_name
        self.attendance_id = attendance_id
        self.date = date
        self.time = time
        self.status = status
        self.already_marked = already_marked
        self.recognition_score = recognition_score
        self.message = message

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "student_id": self.student_id,
            "student_name": self.student_name,
            "attendance_id": self.attendance_id,
            "date": self.date,
            "time": self.time,
            "status": self.status,
            "already_marked": self.already_marked,
            "recognition_score": self.recognition_score,
            "message": self.message
        }


class AttendanceService:
    """
    Implements business policy validations for biometric duplicate checks,
    temporal cooldowns, session mapping, and manual logs administration.
    """
    _instance = None

    @classmethod
    def get_instance(cls, settings=None):
        """
        Singleton accessor.
        """
        if cls._instance is None:
            cls._instance = cls(settings)
        return cls._instance

    def __init__(self, settings=None) -> None:
        self.settings = settings or ConfigLoader.load_config()
        self.repo = AttendanceRepository()
        self.student_repo = StudentRepository()
        
        # Memory cache to tracking recent successful check-ins
        # Format: {student_id: datetime_object_local}
        self.cooldown_cache = {}
        logger.info("AttendanceService initialized successfully.")

    def is_in_cooldown(self, student_id: int) -> bool:
        """
        Checks if the student was marked recently and falls under the active cooldown window.
        """
        if student_id not in self.cooldown_cache:
            return False

        last_time = self.cooldown_cache[student_id]
        diff = get_local_now() - last_time
        
        cooldown_delta = timedelta(minutes=self.settings.cooldown_minutes)
        if diff < cooldown_delta:
            return True

        # Clean cache entry if cooldown expired
        del self.cooldown_cache[student_id]
        return False

    def get_or_create_daily_session(self, date_str: str) -> AttendanceSession:
        """
        Retrieves the active session for the date, or auto-creates a default daily session.
        """
        session = self.repo.get_active_session_by_date(date_str)
        if session:
            return session

        # Auto-create daily session if not configured
        session_data = {
            "name": f"Daily Session - {date_str}",
            "date": date_str,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "status": "Active",
            "created_by": "System"
        }
        logger.info(f"Auto-creating default daily attendance session for: {date_str}")
        return self.repo.create_session(session_data)

    def calculate_status(self, check_in_time: str, session: AttendanceSession) -> str:
        """
        Compares check-in time against the session start time and labels PRESENT or LATE.
        LATE occurs if check_in_time is > session start_time + 15 minutes grace period.
        """
        try:
            check_dt = datetime.strptime(check_in_time, "%H:%M:%S")
            start_dt = datetime.strptime(session.start_time, "%H:%M:%S")
            
            # Grace period defaults to 15 minutes
            late_threshold = start_dt + timedelta(minutes=15)
            
            if check_dt > late_threshold:
                return "LATE"
            return "PRESENT"
        except Exception as e:
            logger.error(f"Error calculating attendance status: {e}")
            return "PRESENT"

    def mark_attendance(
        self,
        student_id: int,
        session_id: int | None = None,
        source: str = "FACE_RECOGNITION",
        status: str | None = None,
        score: float | None = None,
        method: str | None = None,
        time_in: str | None = None,
        date: str | None = None,
        marked_by: str | None = None
    ) -> AttendanceResult:
        """
        Attempts to write a safe attendance entry to the database.
        Includes duplicate checks and cooldown cache blocks.
        """
        # Load student profile
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return AttendanceResult(
                success=False,
                student_id=student_id,
                student_name="Unknown",
                attendance_id=None,
                date=date or get_current_date(),
                time=time_in or get_current_time(),
                status="ABSENT",
                already_marked=False,
                recognition_score=score,
                message="Student profile not found in database."
            )

        student_name = f"{student.first_name} {student.last_name}"
        active_date = date or get_current_date()
        active_time = time_in or get_current_time()

        # 1. Cooldown protection (Only applies to FACE_RECOGNITION source)
        if source == "FACE_RECOGNITION" and self.is_in_cooldown(student_id):
            logger.info(f"Biometric matching for student {student.student_code} skipped due to active cooldown.")
            return AttendanceResult(
                success=True,
                student_id=student_id,
                student_name=student_name,
                attendance_id=None,
                date=active_date,
                time=active_time,
                status="PRESENT",
                already_marked=True,
                recognition_score=score,
                message="Check-in ignored. Cooldown period is active."
            )

        # Retrieve active session
        try:
            if session_id is None:
                session_obj = self.get_or_create_daily_session(active_date)
                session_id = session_obj.id
            else:
                session_obj = self.repo.get_session_by_id(session_id)
                if not session_obj:
                    raise ValueError(f"Session with ID {session_id} does not exist.")
        except Exception as e:
            logger.error(f"Failed to resolve active attendance session: {e}")
            return AttendanceResult(
                success=False,
                student_id=student_id,
                student_name=student_name,
                attendance_id=None,
                date=active_date,
                time=active_time,
                status="ABSENT",
                already_marked=False,
                recognition_score=score,
                message=f"Session unavailable: {e}"
            )

        # 2. Database level duplicate check
        existing_record = self.repo.find_record(student_id, active_date, session_id)
        if existing_record:
            # Update cooldown cache with the current time so we don't spam query DB
            if source == "FACE_RECOGNITION":
                self.cooldown_cache[student_id] = get_local_now()
            
            return AttendanceResult(
                success=True,
                student_id=student_id,
                student_name=student_name,
                attendance_id=existing_record.id,
                date=existing_record.date,
                time=existing_record.time_in,
                status=existing_record.status,
                already_marked=True,
                recognition_score=score,
                message="Attendance already recorded for today's session."
            )

        # Calculate status if not manually specified
        final_status = status or self.calculate_status(active_time, session_obj)

        # Create record dictionary
        record_data = {
            "student_id": student_id,
            "session_id": session_id,
            "date": active_date,
            "time_in": active_time,
            "status": final_status,
            "recognition_score": score,
            "recognition_method": method or ("LBPH" if source == "FACE_RECOGNITION" else None),
            "source": source,
            "updated_by": marked_by
        }

        # 3. Transaction-safe database commit
        try:
            record = self.repo.create_record(record_data)
            
            # Seed cooldown cache on success
            if source == "FACE_RECOGNITION":
                self.cooldown_cache[student_id] = get_local_now()
            
            logger.info(f"Attendance recorded for {student_name} ({student.student_code}): {final_status}")
            return AttendanceResult(
                success=True,
                student_id=student_id,
                student_name=student_name,
                attendance_id=record.id,
                date=record.date,
                time=record.time_in,
                status=record.status,
                already_marked=False,
                recognition_score=score,
                message="Attendance successfully logged."
            )
        except Exception as e:
            logger.error(f"Database error writing attendance log: {e}", exc_info=True)
            return AttendanceResult(
                success=False,
                student_id=student_id,
                student_name=student_name,
                attendance_id=None,
                date=active_date,
                time=active_time,
                status="ABSENT",
                already_marked=False,
                recognition_score=score,
                message=f"Transaction failed: {e}"
            )

    def list_attendance(self, **filters) -> list[Attendance]:
        """
        Retrieves filterable logs list.
        """
        return self.repo.list_attendance(**filters)

    def list_sessions(self) -> list[AttendanceSession]:
        """
        Retrieves all sessions.
        """
        return self.repo.list_sessions()

    def get_today_statistics(self) -> dict:
        """
        Calculates today's attendance summary.
        """
        today = get_current_date()
        session_obj = self.repo.get_active_session_by_date(today)
        session_id = session_obj.id if session_obj else None
        
        stats = self.repo.get_today_statistics(today, session_id)
        
        # Calculate "Not Yet Marked"
        # Total Active Students - Marked Students
        active_students = stats["total_students"]
        marked_count = stats["total_marked"]
        stats["not_marked"] = max(0, active_students - marked_count)
        
        # Session name details
        stats["session_name"] = session_obj.name if session_obj else f"Daily Session - {today}"
        
        return stats

    def get_student_attendance_summary(self, student_id: int) -> dict:
        """
        Fetches student profile stats.
        """
        return self.repo.get_student_attendance_summary(student_id)

    def get_recent_student_records(self, student_id: int, limit: int = 5) -> list[Attendance]:
        """
        Fetches recent logs.
        """
        return self.repo.get_recent_student_records(student_id, limit)

    def update_attendance(self, record_id: int, status: str, updated_by: str) -> tuple[bool, str]:
        """
        Edits an attendance record. Requires manual reason log.
        """
        try:
            update_data = {
                "status": status.upper(),
                "updated_by": updated_by
            }
            self.repo.update_record(record_id, update_data)
            logger.info(f"Attendance ID {record_id} manually updated to status {status} by {updated_by}")
            return True, "Attendance updated successfully."
        except Exception as e:
            logger.error(f"Error modifying attendance record: {e}")
            return False, f"Could not update record: {e}"

    def delete_attendance(self, record_id: int) -> bool:
        """
        Deletes an attendance record.
        """
        return self.repo.delete_record(record_id)
