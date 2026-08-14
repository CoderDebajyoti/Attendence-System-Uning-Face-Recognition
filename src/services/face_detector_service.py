# ==============================================================================
# Face Recognition Attendance System - Face Detector Service
# ==============================================================================

import cv2
import logging

logger = logging.getLogger("app.recognition")

class FaceDetectorService:
    """
    Encapsulates face detection logic using OpenCV Haar Cascade.
    Provides methods to locate bounding boxes and validate suitability for datasets.
    """

    def __init__(self, min_face_size: int = 100, cascade_path: str = None) -> None:
        import os
        from pathlib import Path
        import urllib.request

        self.min_face_size = min_face_size

        if not cascade_path:
            cascade_path = "models/haarcascade_frontalface_default.xml"

        # Check local paths or download
        if not os.path.exists(cascade_path):
            package_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            if os.path.exists(package_path):
                cascade_path = package_path
            else:
                # Ensure directory exists
                parent_dir = os.path.dirname(cascade_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)
                
                logger.info(f"Haar Cascade not found locally. Downloading to: {cascade_path}")
                try:
                    url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
                    urllib.request.urlretrieve(url, cascade_path)
                    logger.info("Download completed successfully.")
                except Exception as e:
                    logger.error(f"Failed to download cascade XML: {e}")

        logger.info(f"Loading Haar Cascade from path: {cascade_path}")
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            logger.error(f"Failed to load Haar Cascade from path: {cascade_path}")
            raise RuntimeError("Haar Cascade XML not found or failed to load.")
        logger.info("FaceDetectorService initialized successfully.")

    def detect_faces(self, image) -> list[tuple[int, int, int, int]]:
        """
        Detects all faces in an image and returns their bounding boxes (x, y, w, h).
        """
        if image is None or image.size == 0:
            return []

        # Convert to grayscale if image is colored
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Detect faces with scale factor and min neighbors
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(self.min_face_size, self.min_face_size)
        )
        # Convert NumPy array results to list of standard tuples
        return [tuple(map(int, face)) for face in faces]

    def validate_face_for_dataset(self, image) -> tuple[bool, str, list[tuple[int, int, int, int]]]:
        """
        Validates that exactly one suitable face is detected in the image.
        Returns:
            is_valid (bool): True if image has exactly one suitable face.
            message (str): Friendly explanation if invalid, else success message.
            boxes (list): The list of face bounding boxes detected.
        """
        if image is None or image.size == 0:
            return False, "Invalid image frame.", []

        height, width = image.shape[:2]
        boxes = self.detect_faces(image)

        # 1. Face Count Validation
        if len(boxes) == 0:
            return False, "Face not detected. Please adjust your position.", []
        if len(boxes) > 1:
            return False, "Multiple faces detected. Please ensure only one person is visible.", boxes

        # Exactly one face
        x, y, w, h = boxes[0]

        # 2. Face Size Validation
        if w < self.min_face_size or h < self.min_face_size:
            return False, f"Face is too small. Please move closer to the camera.", boxes

        # 3. Boundary Check (ensure face is not cropped off/out of bounds)
        if x < 0 or y < 0 or (x + w) > width or (y + h) > height:
            return False, "Face is out of boundary. Please align inside the frame.", boxes

        # 4. Positioning Centering Check
        # Check if the face center is within the middle 60% of the screen horizontally and vertically
        face_center_x = x + w / 2
        face_center_y = y + h / 2
        img_center_x = width / 2
        img_center_y = height / 2

        max_offset_x = width * 0.30
        max_offset_y = height * 0.30

        if abs(face_center_x - img_center_x) > max_offset_x or abs(face_center_y - img_center_y) > max_offset_y:
            return False, "Face is not centered. Please align yourself in the middle.", boxes

        return True, "Face detected. Image captured.", boxes
