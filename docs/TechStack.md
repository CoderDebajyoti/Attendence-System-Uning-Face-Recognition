# Face Recognition Attendance System - Tech Stack Justification

This document details the selected technology stack for the Face Recognition Attendance System. Every component is evaluated for performance, modularity, maintainability, and enterprise readiness.

---

## 1. Selected Stack Summary

| Layer / Concern | Selected Technology | Primary Role | Alternate Evaluated |
| :--- | :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core development language | C++ (high cost), Go (limited AI libs) |
| **Computer Vision** | OpenCV (opencv-python) | Video stream capture, frame manipulation | PyAV, GStreamer (complex setup) |
| **Face Recognition Engine** | InsightFace (ArcFace model) | Detection (RetinaFace), alignment, and feature extraction (512-d embedding) | `face_recognition` (dlib-based), Mediapipe |
| **GUI Framework** | CustomTkinter | Modern desktop graphical interface | PyQt6 / PySide6, wxPython |
| **Database ORM** | SQLAlchemy | Declarative database schema mapper | Peewee, raw SQLite3 |
| **Development Database** | SQLite | Portable local development data store | PostgreSQL, MySQL |
| **Production Database** | PostgreSQL | Scalable network-accessible database | MS SQL, MongoDB |
| **Data Processing** | Pandas | Log analysis, attendance summaries | Pure Python loops |
| **Visualization** | Plotly (embedded as HTML/Tk) | Dynamic dashboard charts and metrics | Matplotlib (static, aged look) |
| **Packaging Utility** | PyInstaller | Compilation into a single executable | Briefcase, PyOxidizer |

---

## 2. Key Architecture Decisions & Justifications

### 2.1 Language: Python 3.10+
- **Why**: Python is the industry standard for computer vision and machine learning. Developing in Python allows us to leverage state-of-the-art model wrappers and optimization frameworks directly. 
- **Design Impact**: Type hinting (`typing` module) is used extensively to enforce code correctness at compile/lint time, bringing structure to a dynamically typed language.

### 2.2 Face Engine: InsightFace vs. face_recognition (dlib)
The face recognition engine is the heart of the system. We selected **InsightFace** over the popular `face_recognition` wrapper. Here is a direct comparative evaluation:

| Criterion | InsightFace (RetinaFace + ArcFace) | face_recognition (dlib HOG + ResNet) |
| :--- | :--- | :--- |
| **Detection Accuracy** | **Superior** (Detects small, rotated, occluded, and poorly lit faces using RetinaFace). | **Moderate** (HOG misses angled faces; CNN detection is very slow on CPU). |
| **Alignment Method** | 5-point affine transformation (standardized normalization). | 68-point landmarks (larger computational footprint). |
| **Embedding Size** | 512-dimensional float vector (higher discrimination capacity). | 128-dimensional float vector (lower accuracy on large datasets). |
| **Inference Runtime** | **ONNX Runtime** (Direct hardware acceleration on CPU/GPU, exceptionally fast execution). | C++ dlib runtime (difficult to compile and package on Windows platforms). |
| **Licensing** | Non-commercial restriction (suitable for educational/internal use). Open-source options exist. | MIT License (permissive). |

- **Decision**: InsightFace is chosen due to its state-of-the-art status and native support for ONNX Runtime. This guarantees high-frame-rate CPU execution and scales easily to GPU hardware.

### 2.3 GUI: CustomTkinter vs. PyQt6 / PySide6
- **Why CustomTkinter**: CustomTkinter extends standard Tkinter with beautiful widgets, dark/light modes, and custom corner rounding. It has zero external compilation dependencies (unlike Qt, which relies on heavy binary files).
- **Justification**: PyQt6 is highly robust but carries strict GPL licensing implications and a steep learning curve. CustomTkinter is lightweight, permissively licensed (MIT), and starts up instantly, offering a native look and feel with minimal bundle overhead.

### 2.4 ORM: SQLAlchemy
- **Why**: Building database-agnostic code is critical for enterprise transition. SQLAlchemy implements the Unit of Work pattern, preventing direct dependencies on specific database flavors.
- **Justification**: In development, we use SQLite (a local serverless file). If a school or enterprise decides to deploy a centralized server, the infrastructure team can switch the database URI to a PostgreSQL instance. The SQLAlchemy ORM mappings handle table creation, indexing, and transactions transparently.

### 2.5 Data Analytics & Visuals: Pandas + Plotly
- **Why**: Instead of custom loop aggregation for monthly attendance statistics, Pandas dataframes allow fast grouping, pivot table creation, and gap checking (e.g., matching scheduled days against logged days).
- **Plotly Integration**: Plotly produces beautiful, interactive charts. By rendering Plotly figures as HTML and embedding them in a Tkinter Webview widget (or displaying static PNG crops in CustomTkinter frames), we provide a premium dashboard experience.
