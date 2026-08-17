# ==============================================================================
# Face Recognition Attendance System - Attendance Analytics Service
# ==============================================================================

import logging
from datetime import datetime, timedelta
from src.core.database import get_session
from src.core.models import Student, Attendance, AttendanceSession, Department, Course
from src.repositories.attendance_repository import AttendanceRepository
from src.utils.time_helper import get_current_date, get_local_now

logger = logging.getLogger("app.analytics")

class AttendanceAnalyticsService:
    """
    Centralized service for generating statistics, attendance rate metrics,
    trends, and summaries across the Dashboard, Reports, and Student Detail views.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self.repo = AttendanceRepository()

    def calculate_attendance_rate(self, present: int, late: int, total_opportunities: int) -> float:
        """
        Standard formula used across the entire application to calculate attendance rate.
        """
        if total_opportunities <= 0:
            return 0.0
        rate = ((present + late) / total_opportunities) * 100.0
        return round(rate, 2)

    def get_daily_statistics(self, date_str: str | None = None) -> dict:
        """
        Aggregates operational metrics for a single date.
        """
        target_date = date_str or get_current_date()
        stats = self.repo.get_today_statistics(target_date)
        
        # Get count of manual vs. recognition entries
        with get_session() as session:
            manual_count = session.query(Attendance).filter(
                Attendance.date == target_date,
                Attendance.source == "MANUAL"
            ).count()
            
            rec_count = session.query(Attendance).filter(
                Attendance.date == target_date,
                Attendance.source == "FACE_RECOGNITION"
            ).count()

        stats["manual_count"] = manual_count
        stats["recognition_count"] = rec_count
        return stats

    def get_date_range_statistics(
        self,
        start_date: str,
        end_date: str,
        department_id: int | None = None,
        course_id: int | None = None,
        student_id: int | None = None
    ) -> dict:
        """
        Aggregates summary metrics across a date range.
        """
        with get_session() as session:
            query = session.query(Attendance).join(Attendance.student)
            
            # Apply filters
            query = query.filter(Attendance.date >= start_date, Attendance.date <= end_date)
            if department_id:
                query = query.filter(Student.department_id == department_id)
            if course_id:
                query = query.filter(Student.course_id == course_id)
            if student_id:
                query = query.filter(Attendance.student_id == student_id)

            records = query.all()
            
            total_records = len(records)
            present = sum(1 for r in records if r.status == "PRESENT")
            late = sum(1 for r in records if r.status == "LATE")
            absent = sum(1 for r in records if r.status == "ABSENT")
            excused = sum(1 for r in records if r.status == "EXCUSED")

            # Determine opportunities:
            # If filtering for a specific student, opportunities is the number of active distinct session dates.
            # If aggregate, opportunities is total_enrolled_students * distinct_session_dates.
            distinct_sessions = session.query(AttendanceSession.date).filter(
                AttendanceSession.date >= start_date,
                AttendanceSession.date <= end_date,
                AttendanceSession.status == "Active"
            ).distinct().count()
            
            if distinct_sessions == 0:
                # Fallback to unique dates present in the attendance records
                distinct_sessions = len(set(r.date for r in records)) or 1

            if student_id:
                total_opportunities = distinct_sessions
            else:
                student_query = session.query(Student).filter(Student.is_active == True, Student.status == "Active")
                if department_id:
                    student_query = student_query.filter(Student.department_id == department_id)
                if course_id:
                    student_query = student_query.filter(Student.course_id == course_id)
                total_enrolled = student_query.count()
                total_opportunities = total_enrolled * distinct_sessions

            # Use total marked if aggregate opportunities cannot be computed or falls to 0
            if total_opportunities <= 0:
                total_opportunities = total_records

            rate = self.calculate_attendance_rate(present, late, total_opportunities)

            return {
                "total_records": total_records,
                "present": present,
                "late": late,
                "absent": absent,
                "excused": excused,
                "opportunities": total_opportunities,
                "rate": rate
            }

    def get_student_statistics(self, student_id: int, start_date: str | None = None, end_date: str | None = None) -> dict:
        """
        Gathers comprehensive statistics for a single student.
        """
        with get_session() as session:
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError("Student not found")
            student_name = f"{student.first_name} {student.last_name}"
            student_code = student.student_code

            query = session.query(Attendance).filter(Attendance.student_id == student_id)
            if start_date:
                query = query.filter(Attendance.date >= start_date)
            if end_date:
                query = query.filter(Attendance.date <= end_date)

            records = query.order_by(Attendance.date.asc(), Attendance.time_in.asc()).all()
            total_records = len(records)
            present = sum(1 for r in records if r.status == "PRESENT")
            late = sum(1 for r in records if r.status == "LATE")
            absent = sum(1 for r in records if r.status == "ABSENT")
            excused = sum(1 for r in records if r.status == "EXCUSED")

            first_attendance = records[0].date if records else "-"
            last_attendance = records[-1].date if records else "-"

            # Opportunities is total marked records
            total_opportunities = present + late + absent + excused
            rate = self.calculate_attendance_rate(present, late, total_opportunities)

            return {
                "student_id": student_id,
                "student_name": student_name,
                "student_code": student_code,
                "total_records": total_records,
                "present": present,
                "late": late,
                "absent": absent,
                "excused": excused,
                "first_attendance": first_attendance,
                "last_attendance": last_attendance,
                "rate": rate
            }

    def get_attendance_trends(self, days_limit: int = 7) -> list[dict]:
        """
        Retrieves date-wise attendance rates for the last N days.
        """
        trends = []
        now = get_local_now()
        
        for i in range(days_limit - 1, -1, -1):
            date_obj = now - timedelta(days=i)
            date_str = date_obj.strftime("%Y-%m-%d")
            day_name = date_obj.strftime("%A")
            
            stats = self.repo.get_today_statistics(date_str)
            trends.append({
                "date": date_str,
                "day_name": day_name,
                "rate": stats["rate"]
            })
        return trends
