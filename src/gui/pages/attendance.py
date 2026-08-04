# ==============================================================================
# Face Recognition Attendance System - Attendance Page View
# ==============================================================================

from src.gui.pages.base import BasePage

class AttendancePage(BasePage):
    """
    Attendance Tracking Page View. Represents Phase 9 Core Attendance Processing.
    """
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            title="Attendance Tracking Panel",
            description="Trigger recognition sessions, monitor check-in events in real-time, and log attendance entries.",
            phase=9
        )
