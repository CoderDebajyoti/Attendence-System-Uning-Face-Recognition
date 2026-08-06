# ==============================================================================
# Face Recognition Attendance System - Deprecated Theme Module
# ==============================================================================

# WARNING: This module is deprecated and will be removed in future phases.
# Please import ThemeManager from src.gui.themes instead.

import logging
from src.gui.themes import ThemeManager

logging.getLogger("app.gui").warning("Importing deprecated src.gui.theme module. Switch to src.gui.themes.ThemeManager.")

# Alias for backward compatibility
Theme = ThemeManager
