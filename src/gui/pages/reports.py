# ==============================================================================
# Face Recognition Attendance System - Reports & Analytics Page View
# ==============================================================================

from src.gui.pages.base import BasePage

class ReportsPage(BasePage):
    """
    Reports Page View. Represents Phase 10 Statistics & Exports.
    """
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            title="Reports & Statistical Analytics",
            description="Export semestral attendance sheets, calculate percentage stats, and review anomalies.",
            phase=10
        )
