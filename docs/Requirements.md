# Face Recognition Attendance System - Requirements Specification

This document details the functional and non-functional requirements of the Face Recognition Attendance System. These requirements serve as the direct foundation for system design, database schemas, and testing strategies.

---

## 1. Functional Requirements (FR)

### 1.1 Student Management
- **FR-1.1.1 (Register Student)**: The system must allow authorized administrators or faculty to register new students with unique IDs, names, email addresses, departments, and course enrollments.
- **FR-1.1.2 (Update Student Details)**: The system must allow modifying student details (except the primary biometric key/ID) and managing their active status.
- **FR-1.1.3 (Delete/Archive Student)**: The system must support deleting a student or setting their status to "Inactive/Archived" to preserve historical attendance data while removing them from active recognition loops.
- **FR-1.1.4 (Search & Filter)**: Users must be able to search for students by Name, ID, Course, or Department.

### 1.2 Faculty Management
- **FR-1.2.1 (Faculty Profiles)**: The system must manage faculty records, including Faculty ID, Name, Department, Email, and designated role.
- **FR-1.2.2 (Class Assignment)**: Faculty members must be linkable to specific courses and subjects they teach.

### 1.3 Admin Management
- **FR-1.3.1 (Role-Based Control)**: System Administrators must have access to global settings, database configuration, system logs, backups, and user management controls (faculty account creation).
- **FR-1.3.2 (Audit Log Viewing)**: Admins must be able to view and export audit trails representing system logins, configuration changes, and manual attendance edits.

### 1.4 Dataset Management
- **FR-1.4.1 (Image Capture Wizard)**: The system must interface with a connected camera to capture a minimum of 5-10 facial images of a student from varying angles (center, slightly left, slightly right, looking up, looking down, smiling, neutral) during enrollment.
- **FR-1.4.2 (Quality Assessment)**: The system must check captured images in real time for quality (e.g., face detection confidence, resolution, and brightness) before adding them to the dataset.
- **FR-1.4.3 (Embedding Generation)**: The system must automatically process the dataset to extract 512-dimensional vector facial embeddings using the Face Recognition Engine and save them under the student's profile.

### 1.5 Face Recognition Engine
- **FR-1.5.1 (Real-time Stream Processing)**: The system must capture video frames from a camera (internal USB or IP Camera RTSP stream).
- **FR-1.5.2 (Face Detection & Alignment)**: The system must detect faces and locate facial landmarks (eyes, nose, mouth) to align the face before extracting embeddings.
- **FR-1.5.3 (Recognition Matcher)**: The system must extract the facial embedding of the detected face and perform a vector similarity search (cosine similarity) against the registered embeddings database.
- **FR-1.5.4 (Threshold Enforcement)**: Recognition is only accepted if the similarity score exceeds a configurable threshold (e.g., 0.65 for Cosine Similarity). If below, the face is labeled "Unknown".

### 1.6 Attendance Marking
- **FR-1.6.1 (Automatic Logging)**: Upon successful recognition, the system must automatically log the student as "Present" for the active course session.
- **FR-1.6.2 (Duplicate Prevention)**: The system must prevent duplicate logs for the same student in the same session within a configurable cooling-off window (e.g., 30 minutes).
- **FR-1.6.3 (Attendance Statuses)**: The system must support statuses: `Present`, `Absent`, `Late`, and `Excused`.

### 1.7 Reports & Analytics
- **FR-1.7.1 (Daily/Monthly Summary)**: The system must generate summaries of attendance records filterable by Department, Course, Subject, Date Range, or Student.
- **FR-1.7.2 (Export Options)**: Faculty must be able to export reports to Microsoft Excel (XLSX) or PDF formats.
- **FR-1.7.3 (Interactive Visualizations)**: The system must display attendance charts (e.g., class attendance percentages over time, top absent students) using Plotly.

### 1.8 Authentication & Authorization
- **FR-1.8.1 (Login/Logout)**: Secure credentials login page for Admin and Faculty.
- **FR-1.8.2 (Password Encryption)**: Securely hash passwords before saving.
- **FR-1.8.3 (Access Limits)**: Prevent Faculty from editing system configs or access logs belonging to other departments.

### 1.9 Settings & Configuration
- **FR-1.9.1 (Camera Selection)**: Choose input camera source index (0, 1, 2) or custom RTSP stream URL.
- **FR-1.9.2 (Recognition Thresholds)**: Configure confidence threshold and cooling-off intervals.
- **FR-1.9.3 (Database Settings)**: Input database connection strings (SQLite path or PostgreSQL credentials).

### 1.10 Notifications
- **FR-1.10.1 (UI Alerts)**: Display instant desktop toast notifications or overlay indicator panels upon recognition (e.g., "Present: John Doe").
- **FR-1.10.2 (Email Alerts - Planned)**: Ability to trigger automated email alerts for students with attendance dropping below the critical threshold (e.g., < 75%).

---

## 2. Non-Functional Requirements (NFR)

### 2.1 Performance
- **NFR-2.1.1 (Latency)**: Face detection, alignment, embedding extraction, and matching database search must take less than 150 milliseconds per frame on standard CPU hardware.
- **NFR-2.1.2 (Frame Rate)**: The camera visualization panel in the UI must render at $\ge 30$ frames per second (FPS) without visual stutter or lag.
- **NFR-2.1.3 (Database Query Speed)**: Bulk attendance reporting queries must return in under 2 seconds for dataset tables up to 100,000 records.

### 2.2 Scalability
- **NFR-2.2.1 (Horizontal Scale)**: The data access layer must support simple swapping from SQLite (local) to PostgreSQL (server-based) via SQLAlchemy environment configuration.
- **NFR-2.2.2 (Dataset Capacity)**: The local system must support up to 5,000 enrolled students and 50,000 embeddings without significant degradation in matching search latency.

### 2.3 Maintainability
- **NFR-2.3.1 (Modular Design)**: Adhere strictly to clean-layered codebase principles (Presentation, Domain/Service, Face Engine, Data Repositories).
- **NFR-2.3.2 (Documentation & Clean Code)**: Code must maintain a 100% docstring coverage matching PEP257 and clean logging statements.

### 2.4 Security
- **NFR-2.4.1 (Biometric Protection)**: Do not expose raw float arrays of face embeddings to clients in plaintext; ensure database access requires local admin privileges.
- **NFR-2.4.2 (Credential Hashing)**: Secure passwords using SHA-256 with salt (or `bcrypt`).
- **NFR-2.4.3 (SQL Injection Prevention)**: Use SQLAlchemy parameter binding for all queries; raw SQL queries are strictly prohibited.

### 2.5 Reliability & Availability
- **NFR-2.5.1 (Fault Tolerance)**: If the camera disconnects, the UI must display a "Camera Disconnected" state gracefully instead of crashing the system.
- **NFR-2.5.2 (Database Connection Retries)**: Implement connection pooling and retry mechanisms for remote database connections.

### 2.6 Portability
- **NFR-2.6.1 (Cross-Platform)**: The application code must run seamlessly on Windows (primary target), macOS, and Linux.
- **NFR-2.6.2 (Packaging)**: Bundlable into a standalone executable (using `PyInstaller`) containing all OpenCV and ONNX runtime runtimes.

### 2.7 Usability
- **NFR-2.7.1 (Sleek UI)**: Modern dark/light theme options using CustomTkinter, with responsive grids adapting to standard desktop resolutions (1280x720 up to 1920x1080).
- **NFR-2.7.2 (Accessibility)**: Legible font contrast ratios and intuitive navigation flows (sidebar navigation).
