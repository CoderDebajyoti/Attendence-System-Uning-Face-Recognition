# Unknown Face Handling

This document details how the recognition engine handles unregistered or unmatched faces.

## Safe Rejections
In attendance monitoring, false positives (wrongly marking the wrong student present) are severe errors. Therefore, the system enforces a strict rejection rule:
- If a detected face's calculated similarity score is below the configuration threshold, the system **must not** return the closest matching student.
- It must explicitly return an **`Unknown`** classification.

## Result Structure
For unmatched faces, `FaceRecognitionService` returns:
- `recognized`: `False`
- `student_id`: `None`
- `student_name`: `"Unknown"`
- `student_code`: `"UNKNOWN"`
- `bounding_box`: `(x, y, w, h)`
- `reason`: `"Similarity score below threshold"`

The GUI draws a **red bounding box** with an `"Unknown"` label to provide instant visual indication that the user is not recognized.
