# ==============================================================================
# Face Recognition Attendance System - PyTest Global Configuration
# ==============================================================================

import os
import sys

# Ensure the 'src' directory is in the import search paths during testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
