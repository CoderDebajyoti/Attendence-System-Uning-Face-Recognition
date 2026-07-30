# Face Recognition Attendance System - Software Architecture

This document describes the high-level software architecture of the Face Recognition Attendance System. The system is designed using a **Layered Architecture pattern** following **Domain-Driven Design (DDD)** and **SOLID** principles. This structure ensures high modularity, ease of testing, and portability.

---

## 1. High-Level Architecture Diagram
The diagram below illustrates the flow of data and dependencies between layers. Dependencies point downwards, ensuring that high-level business rules do not depend on low-level implementation details (Dependency Inversion Principle).

```mermaid
graph TD
    %% Layer definitions
    subgraph Presentation_Layer [Presentation Layer GUI]
        UI[CustomTkinter Main Application]
        VC[View Controllers / State Managers]
        CAM_P[Camera Preview Widget]
        DASH_W[Dashboard & Report Widgets]
    end

    subgraph Service_Layer [Business Logic & Service Layer]
        AUTH_S[Authentication Service]
        STUD_S[Student & Dataset Service]
        ATT_S[Attendance Processing Service]
        REP_S[Report & Analytics Service]
    end

    subgraph Core_Engine [Face Recognition Engine]
        FE_INT[IFaceEngine Interface]
        IFE_IMP[InsightFace Engine Implementation]
        ONNX[ONNX Runtime / CUDA Inference]
    end

    subgraph Data_Access [Data Access Layer ORM]
        REPO[Repository Pattern API]
        SQLA[SQLAlchemy Session Manager]
    end

    subgraph Storage_Layer [Storage Layer]
        DB[(SQLite / PostgreSQL Database)]
        DS[Disk Storage - Raw Dataset Images]
    end

    subgraph Cross_Cutting [Infrastructure & Cross-Cutting Concerns]
        CONF[Configuration Manager]
        LOG[Logging System File/Console]
        TH_M[Threading / Worker Queue Manager]
    end

    %% Dependency Connections
    UI --> VC
    VC --> CAM_P
    VC --> DASH_W
    
    %% Presentation calls Service
    VC --> AUTH_S
    VC --> STUD_S
    VC --> ATT_S
    VC --> REP_S

    %% Service Layer dependencies
    STUD_S --> FE_INT
    ATT_S --> FE_INT
    FE_INT <|-- IFE_IMP
    IFE_IMP --> ONNX

    %% Service calls Repositories
    STUD_S --> REPO
    ATT_S --> REPO
    AUTH_S --> REPO
    REP_S --> REPO

    %% Repo interacts with Database
    REPO --> SQLA
    SQLA --> DB
    STUD_S --> DS

    %% Cross-cutting usages
    VC -.-> TH_M
    STUD_S -.-> CONF
    FE_INT -.-> CONF
    REPO -.-> CONF
    
    classDef layer fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef component fill:#e1f5fe,stroke:#0288d1,stroke-width:1px;
    class Presentation_Layer,Service_Layer,Core_Engine,Data_Access,Storage_Layer,Cross_Cutting layer;
    class UI,VC,CAM_P,DASH_W,AUTH_S,STUD_S,ATT_S,REP_S,FE_INT,IFE_IMP,ONNX,REPO,SQLA,DB,DS,CONF,LOG,TH_M component;
```

---

## 2. Layer Responsibilities

### 2.1 Presentation Layer (GUI)
- **Role**: Handles all user interactions, graphics rendering, and camera stream visualization.
- **Technologies**: CustomTkinter, Matplotlib/Plotly integrations.
- **Design Rationale**: Kept purely decorative and orchestrative. It captures user inputs and feeds them to the Service Layer. It subscribes to background threading events (e.g., face recognized) and updates screens accordingly.

### 2.2 Business Logic / Service Layer
- **Role**: Coordinates the core business workflows. Enforces validation rules (e.g., student name lengths, date logic), schedules check-ins, and calculates aggregate metrics.
- **Components**:
  - `AuthenticationService`: Manages user credentials, login states, and session tokens.
  - `StudentService`: Directs registration, coordinates image collection, and embedding generation.
  - `AttendanceService`: Handles real-time verification logs, filters duplicate scans, and manages active session timers.
  - `ReportService`: Consolidates database records and outputs formatted spreadsheets or charts.

### 2.3 Face Recognition Engine
- **Role**: Encapsulates face detection, landmark alignment, and vector embedding extraction.
- **Design Rationale**: Implements the **Strategy Design Pattern** via the `IFaceEngine` interface. By coding services against an interface rather than a concrete library, we can swap between the high-accuracy `InsightFace` implementation and a lighter `face_recognition` library without modifying a single line of business logic.

### 2.4 Data Access Layer (Repositories)
- **Role**: Abstracts all database queries (CRUD).
- **Design Rationale**: Implements the **Repository Pattern**. Services request data through generic repository interfaces (e.g., `IStudentRepository.get_all_active()`). Under the hood, SQLAlchemy maps these requests to database transactions. This hides SQL syntax, prevents SQL injection, and facilitates moving from SQLite to PostgreSQL.

### 2.5 Storage Layer
- **Role**: Persistent storage of application records and media.
- **Components**:
  - **Relational DB**: Stores structured records (students, course maps, check-in timestamps, users).
  - **File System**: Holds face enrollment datasets (original aligned image crops) organized by Student ID.

---

## 3. Infrastructure & Cross-Cutting Concerns

### 3.1 Threading & Worker Queue Manager
- **Why it exists**: Video capture and deep-learning model inference are computationally heavy and block-bound. Running them on the main GUI thread causes UI freezing.
- **Mechanism**:
  - Main thread initializes CustomTkinter and handles UI frames.
  - An independent `CameraCaptureWorker` thread reads frames from the camera and stores them in a raw frame queue.
  - An independent `InferenceWorker` thread reads frames, detects faces, extracts embeddings, searches the DB, and places matching results into a UI update queue.
  - A thread-safe timer event in CustomTkinter polls the update queue at 30ms intervals to update canvas images and show recognition alerts.

### 3.2 Configuration Manager
- **Role**: Loads, validates, and writes system configuration parameters from/to a secure local JSON or YAML file (`config.json`). Contains camera sources, server URLs, threshold levels, and styling configurations.

### 3.3 Logging Strategy
- **Role**: Centralized system diagnostics and auditing.
- **Design**: Python’s native `logging` module is configured with rolling file handlers. The system outputs logs into distinct channels:
  1. `app_system.log`: General debugging, startup sequences, configuration changes, and errors.
  2. `face_recognition.log`: Embedding matcher timings, threshold misses, and unknown faces detection.
  3. `audit_trail.log`: Secure database modifications, manual edits to logs, and faculty logins (highly compliance-focused).
