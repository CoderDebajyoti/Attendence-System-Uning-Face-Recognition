# ==============================================================================
# Face Recognition Attendance System - System Settings Page View
# ==============================================================================

from src.gui.pages.base import BasePage

class SettingsPage(BasePage):
    """
    Settings Page View. Represents Phase 1 Configurations UI.
    """
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            title="System Configurations",
            description="Manage environment variables, recognition confidence metrics, secret keys, and database connections.",
            phase=1
        )
