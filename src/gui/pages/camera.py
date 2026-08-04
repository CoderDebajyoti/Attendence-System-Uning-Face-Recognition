# ==============================================================================
# Face Recognition Attendance System - Camera Configurations Page View
# ==============================================================================

from src.gui.pages.base import BasePage

class CameraPage(BasePage):
    """
    Camera Configuration Page View. Represents Phase 5 Camera Management.
    """
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            title="Camera Stream Setup",
            description="Configure video interfaces, resolution properties, FPS settings, and test frame connection streams.",
            phase=5
        )
