# Face Recognition Testing

This document details the validation strategies and tests implemented for the Face Recognition Engine.

## Testing Architecture
Unit tests are placed under `tests/unit/test_recognition_service.py` and run using `pytest`.

## Mocking Strategy
To ensure tests can run in headless CI environments or hosts lacking webcam peripherals:
1. **Camera Mocking**: OpenCV's `cv2.VideoCapture` is mocked using `unittest.mock.patch` to return predetermined frames, bypass physical camera checks, and fail immediately for negative tests.
2. **Recognizer Mocking**: To bypass C++ read-only binding limitations on `cv2.face.LBPHFaceRecognizer` attributes, we patch the factory instantiation `cv2.face.LBPHFaceRecognizer_create` to return mock recognizer instances.

## Key Scenarios Tested
- **Grayscale Preprocessing**: Verifies input frames are cropped, resized to 112x112, and grayscaled correctly.
- **Model Build / Save / Load**: Checks model compilation from ready database datasets and loads XML + JSON metadata.
- **Matching Telemetry**: Simulates a high similarity score ($0.90 \ge 0.65$) to verify correct student mapping.
- **Rejection Threshold**: Simulates a low match score ($0.40 < 0.65$) to ensure the student is marked as `"Unknown"`.
- **Outdated Model Triggers**: Simulates updating a dataset in the database and checks that model status changes to `OUTDATED`.
