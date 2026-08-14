# ==============================================================================
# Face Recognition Attendance System - Image Processing Service
# ==============================================================================

import cv2
import os
import numpy as np
import logging

logger = logging.getLogger("app.recognition")

class ImageProcessingService:
    """
    Handles image processing logic: cropping, resizing, normalization,
    quality checking (brightness, blurriness), and safe filesystem storage.
    """

    def __init__(self, target_size: tuple[int, int] = (112, 112)) -> None:
        self.target_size = target_size
        logger.info(f"ImageProcessingService initialized with target size: {target_size}")

    def crop_and_resize(self, image, box: tuple[int, int, int, int]) -> np.ndarray:
        """
        Crops the face bounding box and resizes it to the target dimensions.
        """
        x, y, w, h = box
        # Ensure coordinates are within image boundaries
        height, width = image.shape[:2]
        x_start = max(0, x)
        y_start = max(0, y)
        x_end = min(width, x + w)
        y_end = min(height, y + h)

        crop = image[y_start:y_end, x_start:x_end]
        resized = cv2.resize(crop, self.target_size, interpolation=cv2.INTER_AREA)
        return resized

    def check_quality(self, crop) -> tuple[bool, str]:
        """
        Checks the quality of the cropped face image:
        - Brightness check: mean pixel value.
        - Blurriness check: Laplacian variance.
        """
        if crop is None or crop.size == 0:
            return False, "Empty image crop."

        # Convert to grayscale for analysis
        if len(crop.shape) == 3:
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        else:
            gray = crop

        # 1. Brightness check
        mean_brightness = gray.mean()
        if mean_brightness < 45:
            return False, "Face crop is too dark. Please improve lighting."
        if mean_brightness > 230:
            return False, "Face crop is too bright. Please reduce glare/light source."

        # 2. Blurriness (sharpness) check
        # Compute Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 50.0:  # Sensible threshold for small 112x112 crops
            return False, "Image is too blurry. Please remain still."

        return True, "Quality check passed."

    def save_image(self, image, file_path: str) -> bool:
        """
        Saves the processed crop safely to the filesystem.
        """
        try:
            # Create parent directories if they don't exist
            dir_name = os.path.dirname(file_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)

            # Save the image using OpenCV
            success = cv2.imwrite(file_path, image)
            if not success:
                logger.error(f"Failed to write image to: {file_path}")
                return False

            logger.info(f"Successfully saved image: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Exception during saving image to {file_path}: {e}")
            return False
