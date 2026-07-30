# Face Recognition Attendance System - Service API Planning

This document details the internal service interfaces for the application. Although this is a desktop application, designing these interfaces decoupling the business logic from GUI widgets allows for unit testing, future web API migration, and clean implementation separation.

---

## 1. Authentication Service Interface

- **Module**: `src.services.auth_service`
- **Responsibility**: Handles user logins, validates credentials, encrypts new accounts, and tracks active session states.

```python
from typing import Optional, Dict, Any

class IAuthenticationService:
    def login(self, username_or_email: str, password_hash: str) -> bool:
        """
        Validates login credentials. On success, sets active session state.
        
        :param username_or_email: Username string or registered email.
        :param password_hash: Plaintext password from UI entry (hashed internally).
        :return: True if credentials are valid, False otherwise.
        """
        pass

    def logout(self) -> None:
        """
        Terminates the active session and clears user credentials from memory.
        """
        pass

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves detail payload of the currently logged-in user.
        
        :return: Dict of user keys (id, username, role, department) or None.
        """
        pass

    def create_user(self, username: str, email: str, password_hash: str, role_id: int) -> int:
        """
        Registers a new system user (Admin/Faculty). (Admin only).
        
        :return: The generated user ID database integer.
        """
        pass
```

---

## 2. Student Service Interface

- **Module**: `src.services.student_service`
- **Responsibility**: Manages student details, coordinates the registration workflow, and controls dataset image management.

```python
from typing import List, Dict, Any, Optional

class IStudentService:
    def register_student(self, details: Dict[str, Any]) -> int:
        """
        Creates a new student record in database.
        
        :param details: Key-value map (student_code, first_name, last_name, course_id).
        :return: The generated student ID.
        """
        pass

    def update_student(self, student_id: int, updates: Dict[str, Any]) -> bool:
        """
        Modifies properties of an existing student.
        """
        pass

    def get_student_by_code(self, student_code: str) -> Optional[Dict[str, Any]]:
        """
        Queries student profile by their unique organization code.
        """
        pass

    def search_students(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Queries and filters student directories.
        
        :param filters: Search parameters (name, department_id, course_id, status).
        :return: List of matching student records.
        """
        pass

    def delete_student_biometrics(self, student_id: int) -> bool:
        """
        Deletes facial embeddings and physical crop datasets linked to a student.
        """
        pass
```

---

## 3. Face Recognition Service Interface

- **Module**: `src.core.interfaces.face_engine`
- **Responsibility**: Coordinates face detection, affine warp alignment, and feature vector extraction.

```python
import numpy as np
from typing import List, Dict, Any, Tuple

class IFaceEngine:
    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Scans a image frame to locate bounding boxes and 5-point landmarks.
        
        :param image: BGR image frame read via OpenCV.
        :return: List of detected face maps containing 'box' and 'landmarks'.
        """
        pass

    def align_face(self, image: np.ndarray, landmarks: List[Tuple[float, float]]) -> np.ndarray:
        """
        Applies similarity affine transformation to rotate and crop the face.
        
        :param image: Original source frame.
        :param landmarks: 5 key landmarks (eyes, nose, mouth).
        :return: Cropped $112x112$ aligned BGR image face patch.
        """
        pass

    def extract_embedding(self, aligned_face: np.ndarray) -> np.ndarray:
        """
        Passes aligned patch through ArcFace ONNX model to get 512-d float vector.
        
        :param aligned_face: Aligned $112x112$ BGR face patch.
        :return: 1D NumPy array of 512 float values (L2 Normalized).
        """
        pass
```

---

## 4. Embedding Service Interface

- **Module**: `src.services.embedding_service`
- **Responsibility**: Manages vector CRUD operations, similarity queries, and matching logic.

```python
import numpy as np
from typing import Optional, Tuple

class IEmbeddingService:
    def save_embedding(self, student_id: int, embedding: np.ndarray, image_path: str) -> int:
        """
        Serializes and writes a 512-d vector to the database.
        """
        pass

    def find_nearest_match(self, query_embedding: np.ndarray, threshold: float) -> Tuple[Optional[int], float]:
        """
        Compares query vector against all database vectors using dot product.
        
        :param query_embedding: 512-d query vector.
        :param threshold: Minimum Cosine similarity cutoff.
        :return: Tuple of (Matched Student ID or None, Similarity score float).
        """
        pass
```

---

## 5. Attendance Service Interface

- **Module**: `src.services.attendance`
- **Responsibility**: Tracks system scans, prevents duplicate inputs, filters cooling-off checks, and registers manual entries.

```python
from datetime import date, time
from typing import List, Dict, Any

class IAttendanceService:
    def verify_and_log(self, student_id: int, subject_id: int) -> Dict[str, Any]:
        """
        Verifies student status, runs cooldown checks, and logs attendance.
        
        :return: Dict indicating action outcome (Logged, SkippedDuplicate, Error).
        """
        pass

    def log_unknown_attempt(self, similarity_score: float, file_path: str) -> None:
        """
        Logs a low-confidence or unknown face recognition event for audit review.
        """
        pass

    def edit_attendance_record(self, record_id: int, status: str, editor_user_id: int) -> bool:
        """
        Performs manual override updates. Writes record to log and audit trail.
        """
        pass
```

---

## 6. Report Service Interface

- **Module**: `src.services.report_service`
- **Responsibility**: Groups attendance data, runs Pandas statistical calculations, and exports files.

```python
from datetime import date
from typing import List, Dict, Any

class IReportService:
    def generate_summary(self, subject_id: int, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """
        Aggregates attendance metrics per student within date ranges.
        
        :return: List containing student names, rates, classes present, and absences.
        """
        pass

    def export_to_excel(self, data: List[Dict[str, Any]], output_path: str) -> bool:
        """
        Formats report output sheet as a spreadsheet (.xlsx) using Pandas.
        """
        pass

    def export_to_pdf(self, data: List[Dict[str, Any]], output_path: str) -> bool:
        """
        Generates formal corporate PDF grids containing summary charts.
        """
        pass
```
