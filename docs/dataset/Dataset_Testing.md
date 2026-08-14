# Face Dataset Testing Suite

This document explains the testing strategy and execution plan for the Face Dataset module.

---

## Unit Testing Strategy

To avoid requiring physical camera hardware during testing, the unit tests use mocks:

1.  **Database Sessions**: Uses an in-memory SQLite database (`sqlite:///:memory:`) to verify queries without modifying production databases.
2.  **Camera & Video Mocks**: Replaces actual camera frames with mock NumPy arrays (`np.zeros`) and mocks the return values of cv2 functions (e.g. `cv2.imread`).
3.  **Audit Checks Mocking**: Mocks quality control results (sharpness, brightness) and face alignment bounds to simulate successful and failing runs.

---

## Test Cases Covered

The test suite in `tests/unit/test_dataset_service.py` verifies:
*   **Lazy Creation**: Fetching or creating a dataset correctly instantiates database records.
*   **Capture Success**: Processing and saving a valid face transitions the status to `COLLECTING` and increments the count.
*   **Capture Rejection**: Zero or multiple faces are rejected, and invalid frames are not saved.
*   **Image Deletion**: Deleting an image deletes the file, removes database rows, and updates counters.
*   **Clear Dataset**: Wiping a dataset removes the files and resets the student's status to `NOT_REGISTERED`.
*   **Validation Checklist**: Verifies the audit checks fail when images are insufficient or invalid, and succeed when they meet the target count (25).

---

## Running the Tests

Execute this command to run the unit test suite:
```powershell
.venv\Scripts\python -m pytest tests/unit/test_dataset_service.py -v
```
