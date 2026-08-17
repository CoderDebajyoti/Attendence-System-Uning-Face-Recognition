# ==============================================================================
# Face Recognition Attendance System - Centralized Time Utility
# ==============================================================================

from datetime import datetime, timezone

def get_utc_now() -> datetime:
    """
    Returns the current UTC datetime as a timezone-aware object (Python 3.12+ safe).
    """
    return datetime.now(timezone.utc)

def get_local_now() -> datetime:
    """
    Returns the current local datetime.
    """
    return datetime.now()

def get_current_date() -> str:
    """
    Returns the current local date in YYYY-MM-DD format.
    """
    return get_local_now().strftime("%Y-%m-%d")

def get_current_time() -> str:
    """
    Returns the current local time in HH:MM:SS format.
    """
    return get_local_now().strftime("%H:%M:%S")

def format_display_time(time_str: str) -> str:
    """
    Converts 'HH:MM:SS' time string to user-friendly format (e.g. '09:12 AM').
    """
    try:
        dt = datetime.strptime(time_str, "%H:%M:%S")
        return dt.strftime("%I:%M %p")
    except ValueError:
        return time_str
