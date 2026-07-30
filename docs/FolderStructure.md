# Face Recognition Attendance System - Folder Structure

To support clean maintenance, scaling, and testing, the codebase is structured around a multi-package Python layout. This structure strictly separates the GUI presentation, business logic services, face recognition engine, and data access layers.

---

## 1. Directory Tree Diagram

Below is the directory map of the project repository:

```text
Face-Recognition-Attendance-System/
│
├── .github/                   # GitHub workflows, issue templates, and CI/CD pipelines
│   └── workflows/
│       ├── test.yml           # Runs pytest on push/PR
│       └── release.yml        # Automates PyInstaller builds for releases
│
├── assets/                    # Shared assets for root README and global items
│   └── diagrams/
│
├── config/                    # Configuration template files and environment parameters
│   ├── config.default.yaml    # Default application config templates
│   └── logging.config.json    # Logging formats and log rotation settings
│
├── data/                      # Local database and dataset storage (Git Ignored in production)
│   ├── app_database.db        # Default SQLite development database
│   ├── datasets/              # Folder containing aligned face crop images (Subfolders by Student ID)
│   └── backups/               # Local database backups
│
├── docs/                      # Comprehensive system documentation
│
├── src/                       # Main application source code
│   ├── __init__.py
│   ├── main.py                # Main application entry point
│   │
│   ├── core/                  # Core Interfaces, Entities and Computer Vision components
│   │   ├── __init__.py
│   │   ├── exceptions.py      # Custom application exception definitions
│   │   ├── interfaces/        # Abstract Base Classes (ABCs) for decoupling
│   │   │   ├── __init__.py
│   │   │   ├── face_engine.py # Abstract IFaceEngine interface
│   │   │   └── repository.py  # Abstract Repository patterns (IRepository)
│   │   │
│   │   └── face_engine/       # Concrete Face Detection and Embedding generators
│   │       ├── __init__.py
│   │       ├── factory.py     # Instantiates the engine implementation based on config
│   │       ├── insightface.py # InsightFace implementation of IFaceEngine
│   │       └── dlib_compat.py # Backup face_recognition/dlib implementation
│   │
│   ├── services/              # Pure Business Logic / Application Coordination Layer
│   │   ├── __init__.py
│   │   ├── auth_service.py    # Admin/Faculty login, hashing verification, session management
│   │   ├── student_service.py # Student registration coordinates and dataset creation
│   │   ├── attendance.py      # Attendance log manager, cooling-off validation, automatic checks
│   │   └── report_service.py  # Generates reports (Pandas processing, CSV/Excel/PDF exporters)
│   │
│   ├── data_access/           # Data Access Layer (DAL) ORM and Repositories
│   │   ├── __init__.py
│   │   ├── connection.py      # SQLAlchemy engine setup, session factories, and connection pools
│   │   ├── models.py          # SQLAlchemy Declarative Models (DeclarativeBase)
│   │   └── repositories/      # Concrete implementations of core database repositories
│   │       ├── __init__.py
│   │       ├── base.py        # Generic base SQL repository implementation
│   │       ├── student_repo.py
│   │       ├── attendance_repo.py
│   │       └── user_repo.py
│   │
│   ├── ui/                    # Presentation Layer (CustomTkinter Desktop Application)
│   │   ├── __init__.py
│   │   ├── app.py             # Main Application Window and Frame Switcher
│   │   ├── assets/            # UI specific themes, icons, and custom fonts
│   │   │   ├── themes/        # CustomTkinter .json theme configuration files
│   │   │   └── icons/         # PNG/SVG icons for buttons and panels
│   │   │
│   │   ├── components/        # Reusable custom UI components and widgets
│   │   │   ├── __init__.py
│   │   │   ├── camera_panel.py# Frame processing canvas overlay widget
│   │   │   ├── stat_card.py   # Modern KPIs display cards
│   │   │   └── data_table.py  # Paginated, filterable grid component
│   │   │
│   │   └── views/             # Individual Page View Frames (State Managers)
│   │       ├── __init__.py
│   │       ├── login.py       # Login screen controller
│   │       ├── dashboard.py   # Main statistics and quick actions dashboard
│   │       ├── students.py    # Student list, enroll interface, capture wizard
│   │       ├── attendance.py  # Real-time scan engine control view
│   │       ├── reports.py     # Filterable analysis table and export options view
│   │       └── settings.py    # Camera settings, thresholds, DB connections view
│   │
│   └── utils/                 # General Utility helper modules
│       ├── __init__.py
│       ├── logger.py          # Setup script for rolling files and console output streams
│       ├── image_helpers.py   # OpenCV helpers (resizing, alignment, rotation)
│       └── threading.py       # Thread workers, queue handlers, and lock objects
│
├── tests/                     # Standardized test suites (PyTest)
│   ├── __init__.py
│   ├── conftest.py            # Shared fixtures (In-memory SQLite setup, Mock engines)
│   ├── unit/                  # Tests isolating single functions or classes (mocks used)
│   │   ├── test_auth.py
│   │   ├── test_attendance.py
│   │   └── test_face_engine.py
│   ├── integration/           # Tests checking cooperation between services and database
│   │   └── test_registration_flow.py
│   └── performance/           # Benchmarking scripts
│       └── test_matcher_latency.py
│
├── .gitignore                 # Specifies intentionally untracked files to ignore
├── LICENSE                    # Open-source MIT License
├── README.md                  # Project overview and installation guide
├── pyproject.toml             # Python package build configurations
├── requirements.txt           # Production package dependencies
└── requirements-dev.txt       # Testing and validation dependencies
```

---

## 2. Directory Rationale

### 2.1 The `src/` Directory
All execution code is kept inside `src/`. This prevents namespace pollution and enforces a standard packaging structure. Running test tools or linters outside `src/` ensures that tests only run against installed or packaging-ready modules.

### 2.2 `core/` vs `services/`
- **`core/`** houses components that define *what* the system does conceptually (interfaces) and the raw computer vision algorithms (face recognition). It has zero knowledge of databases or GUI layouts.
- **`services/`** is the application coordinator. It contains the business rules. For example, when registering a student, the `student_service.py` receives a request, uses the `IFaceEngine` to extract embeddings from captured images, writes them using a student repository, and logs the action.

### 2.3 `data_access/` (DAL)
Contains the SQLAlchemy model mapping schemas. Splitting models (`models.py`) from repository access patterns (`repositories/`) prevents database connection setups or direct SQL operations from bleeding into the services layer. If PostgreSQL migration happens, only the connection config changes, while repository classes adapt transparently.

### 2.4 `ui/`
The UI directory contains views and widgets. Storing reusable elements like the video viewer canvas in `ui/components/` makes pages in `ui/views/` lighter and cleaner. View files focus on layout and state management, communicating with the back-end services asynchronously.
