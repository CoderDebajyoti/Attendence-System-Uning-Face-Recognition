# Face Detection & Verification

This document details the face verification engine implemented in the `FaceDetectorService`.

---

## Face Detector Engine

The module uses OpenCV's Cascade Classifier architecture to detect frontal faces in real-time.

### Path Resolution & Auto-Download
To maximize portability, the detector looks for the Haar Cascade model XML file (`haarcascade_frontalface_default.xml`) in these locations sequentially:
1.  Local Workspace models directory (`models/haarcascade_frontalface_default.xml`).
2.  OpenCV package path (`cv2.data.haarcascades`).
3.  **Automatic Fallback**: If missing in both, it downloads the official file from the OpenCV raw GitHub repository and saves it to `models/` for future offline runs.

---

## Validation Pipeline Checks

A face crop is saved only if it passes these tests:

### 1. Singular Face check
*   **0 faces detected**: Returns `"Face not detected. Please adjust your position."`
*   **> 1 faces detected**: Returns `"Multiple faces detected. Please ensure only one person is visible."`

### 2. Dimension constraints
*   The bounding box must have a width and height of at least **100px** (or the customized minimum face size).

### 3. Boundary check
*   Ensures that the face is completely inside the frame and not cut off by the edges of the image.

### 4. Centering check
*   Calculates the center of the bounding box $(cx, cy)$ and compares it to the center of the camera frame $(gx, gy)$.
*   The face is rejected if it deviates horizontally or vertically by more than **30%** of the frame dimensions.
