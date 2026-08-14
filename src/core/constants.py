# ==============================================================================
# Face Recognition Attendance System - Global System Constants
# ==============================================================================

# --- Computer Vision & Alignment Settings ---
IMAGE_CHANNELS = 3
FACE_ALIGN_SIZE = 112            # standard InsightFace/ArcFace input size
EMBEDDING_DIM = 512              # length of ArcFace float feature vector

# --- Default Calibration Values ---
DEFAULT_RECOGNITION_THRESHOLD = 0.65
DEFAULT_COOLDOWN_MINUTES = 30
DEFAULT_CAMERA_FPS = 30
DEFAULT_TARGET_IMAGE_COUNT = 25

# --- Graphic Customizations ---
THEME_LIGHT = "light"
THEME_DARK = "dark"
THEME_SYSTEM = "system"

DEFAULT_THEME = THEME_DARK
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 768

# --- System Logs Layouts ---
AUDIT_TRAIL_LOGGER = "app.audit"
SYSTEM_DIAG_LOGGER = "app.system"
CV_ENGINE_LOGGER = "app.recognition"
