# Face Recognition Attendance System - Development Roadmap

This document outlines the phased roadmap for developing, testing, and deploying the Face Recognition Attendance System.

---

## Roadmap Overview

```mermaid
gantt
    title Face Recognition Attendance System Gantt
    dateFormat  YYYY-MM-DD
    section Core Infrastructure
    Phase 0: Planning & Blueprinting :done, p0, 2026-07-01, 7d
    Phase 1: Project Setup & Linting  :done, p1, after p0, 3d
    Phase 2: Database & SQLAlchemy ORM :active, p2, after p1, 5d
    Phase 3: Auth & Cryptography      :p3, after p2, 4d
    section Domain & CV Pipelines
    Phase 4: Student & Course CRUD    :p4, after p3, 5d
    Phase 5: Dataset Capturer Wizard  :p5, after p4, 6d
    Phase 6: Face Inference Engine    :p6, after p5, 7d
    Phase 7: Real-time Process Loop   :p7, after p6, 8d
    section Interface & Reports
    Phase 8: UI Views & CustomTkinter :p8, after p7, 8d
    Phase 9: Analytics & Exporters    :p9, after p8, 5d
    Phase 10: Distributing & Executable:p10, after p9, 4d
```

---

## Phase Specifications

### Phase 0: Planning & Architecture
- **Objective**: Establish the software architecture blueprint, database structures, and testing strategies.
- **Deliverables**: Comprehensive Markdown documentation in the `docs/` folder.
- **Dependencies**: None.
- **Complexity**: Low.
- **Success Criteria**: All planning documents approved and integrated with git controls.

### Phase 1: Project Setup & Environment Configuration
- **Objective**: Configure Python development workspaces, dependencies files, pre-commit styling hooks, and CI workflows.
- **Deliverables**: `.gitignore`, `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, and GitHub Actions workflow scripts.
- **Dependencies**: Phase 0.
- **Complexity**: Low.
- **Success Criteria**: Linter suites (`black`, `flake8`) run cleanly, and empty repository builds successfully on GitHub actions runners.

### Phase 2: Database Layer & Migrations
- **Objective**: Construct SQLAlchemy schemas, repositories API classes, database engine links, and database migration contexts.
- **Deliverables**: `src/data_access/models.py`, `src/data_access/connection.py`, base repositories interfaces, and initialized Alembic configurations.
- **Dependencies**: Phase 1.
- **Complexity**: Medium.
- **Success Criteria**: Automated schema creation passes; integration tests verify database connections, inserts, updates, and rollback actions.

### Phase 3: Authentication & Security
- **Objective**: Implement secure user profile creation (Admin/Faculty) utilizing password hashing.
- **Deliverables**: `src/services/auth_service.py` implementing `IAuthenticationService`, passwords verification tests using `bcrypt`.
- **Dependencies**: Phase 2.
- **Complexity**: Low.
- **Success Criteria**: Hashed strings successfully save in DB. Login validations return correct booleans and raise session validations.

### Phase 4: Student & Faculty Management
- **Objective**: Develop course registries and student profile management operations.
- **Deliverables**: `src/services/student_service.py` implementing CRUD operations; repository interfaces (`student_repo.py`).
- **Dependencies**: Phase 3.
- **Complexity**: Low.
- **Success Criteria**: Student profiles successfully insert into database, link correctly to course departments, and support active filtering searches.

### Phase 5: Dataset Capture Wizard
- **Objective**: Configure camera frame readers and save cropped face arrays.
- **Deliverables**: `src/utils/image_helpers.py` (cropping, illumination adjustments) and dataset directory management scripts.
- **Dependencies**: Phase 4.
- **Complexity**: Medium.
- **Success Criteria**: Capture script reads 10 frame captures of a user, crops faces, and writes crops to `data/datasets/<student_id>/`.

### Phase 6: Face Recognition Inference Engine
- **Objective**: Implement face detection, affine landmark alignments, and vector extraction using InsightFace.
- **Deliverables**: `src/core/face_engine/insightface.py` implementing `IFaceEngine`, ONNX model weight files loader scripts.
- **Dependencies**: Phase 5.
- **Complexity**: High.
- **Success Criteria**: System aligns a face, extracts a 512-dimensional vector embedding, and similarity scans return accuracy scores in $<120\text{ms}$.

### Phase 7: Real-time Attendance Logging Engine
- **Objective**: Orchestrate background worker threads and matching cooldown filters.
- **Deliverables**: `src/services/attendance.py` implementing `IAttendanceService`, thread managers (`src/utils/threading.py`).
- **Dependencies**: Phase 6.
- **Complexity**: High.
- **Success Criteria**: Video capture reads at 30 FPS on a background thread without blocking the main thread, successfully matching faces and writing "Present" states to database logs.

### Phase 8: Dashboard & User Interface
- **Objective**: Assemble the CustomTkinter desktop interface containing sidebar menus and visual pages.
- **Deliverables**: `src/ui/app.py` and views scripts (`login.py`, `dashboard.py`, `students.py`, `attendance.py`, `settings.py`).
- **Dependencies**: Phase 7.
- **Complexity**: Medium.
- **Success Criteria**: GUI runs seamlessly at native framerates, handles views transitions correctly, and displays real-time video frames on the canvas.

### Phase 9: Reports & Analytical Visuals
- **Objective**: Build analytics reports and export templates.
- **Deliverables**: `src/services/report_service.py` utilizing Pandas and exporting XLS/PDF reports.
- **Dependencies**: Phase 8.
- **Complexity**: Medium.
- **Success Criteria**: Faculty can export attendance reports to Excel and PDF formats, showing aggregated percentages.

### Phase 10: Compilation & Deployment
- **Objective**: Build standalone binaries and compile release packages.
- **Deliverables**: Executable packaging script `app.spec`, compiled installers, and project installation guides.
- **Dependencies**: Phase 9.
- **Complexity**: Medium.
- **Success Criteria**: Compiled application runs on clean target machines without requiring Python installations, opening immediately into the login screen.
