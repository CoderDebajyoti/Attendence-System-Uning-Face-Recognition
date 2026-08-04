# ==============================================================================
# Face Recognition Attendance System - About Page View
# ==============================================================================

from src.gui.pages.base import BasePage

class AboutPage(BasePage):
    """
    About Page View. Displays system metrics and copyright information.
    """
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            title="About System",
            description="Version information, development roadmap status, and license details.",
            phase=1
        )
