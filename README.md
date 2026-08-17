# AI-Powered Face Recognition Attendance System

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A secure, contactless, AI-powered desktop attendance tracking system using **Python 3.12+**, **OpenCV Haar Cascades**, **OpenCV LBPH Face Recognizer**, **SQLAlchemy**, and **CustomTkinter**.

---

## 📖 Project Overview

Traditional attendance recording systems (manual rolls, card swipes, barcodes) suffer from proxy logs ("buddy punching"), wear and tear on physical cards, and time overhead. 

This repository implements a **decoupled, multi-threaded facial tracking terminal** designed for schools, universities, training institutes, and modern workspaces. Utilizing OpenCV Haar Cascade classifiers for face detection and OpenCV's LBPH Face Recognizer for biometric template matching, the system automatically checks in students in real time as they walk past the camera feed, ignoring duplicate matches via configurable cooldown windows and writing logs securely to SQLite database files.

---

## ⚡ Core Features
*   **Secure Authentication**: Boots directly to a login page. On the very first run (with an empty database), a setup wizard guides the creation of the initial administrator account. Credentials are encrypted and verified using `bcrypt` salting and hashing.
*   **Asynchronous Camera Processing**: Camera reading and face inference run on background threads, keeping visual UI updates at a smooth 30+ FPS.
*   **Optimized Biometric Loop**: Implements a cached singleton face detector pattern to eliminate repeating disk parsing overhead and maximize processing performance.
*   **Decoupled Architecture**: All controllers and services are fully separated from the visual layout views to simplify testing and code evolution.
*   **Dynamic Logs Display**: The dashboard log tracer panel pulls system diagnostics events from the active log files (`logs/app_system.log`) in real time.
*   **Spreadsheet Analytics Exporters**: Built-in reports service utilizing Python libraries to calculate monthly statistics and export aggregates directly into formatted Microsoft Excel and CSV files.
*   **Clean 8-Page Layout**: Contains only completed views. Menu links are restricted to:
    1.  **Dashboard**: Operational counts, biometric stats, and real-time logs display.
    2.  **Students**: Registering student profiles, search, filter, and CRUD operations.
    3.  **Dataset**: Capture and cropping templates wizard.
    4.  **Recognition**: Real-time camera biometric tracking feed.
    5.  **Attendance**: Override registers and logs correction view.
    6.  **Reports**: Exporters configuration and dynamic statistics preview.
    7.  **Settings**: GUI form to configure thresholds, directories, log level, and local webcam indices (includes a camera connection live stream viewfinder test popup).
    8.  **About**: Operational versions metadata and core tech stack parameters.

---

## 🛠️ Technology Stack
*   **Language**: Python 3.12+
*   **Computer Vision**: OpenCV (`opencv-python`)
*   **Graphical Interface**: CustomTkinter
*   **Database Management**: SQLite with SQLAlchemy ORM
*   **Password Hashing**: Bcrypt
*   **Excel Writing**: OpenPyXL
*   **Testing Suite**: pytest (unit & repository integration coverage)

---

## 📂 Repository Folder Structure

```text
Face-Recognition-Attendance-System/
├── docs/                      # Architectural designs and guides
├── database/                  # SQLite storage, backups, and dataset crops
├── logs/                      # System diagnostic logs & audit trails
├── models/                    # AI Haar Cascade files directory
├── requirements/              # Segmented dependency listings
├── src/                       # Source code root
│   ├── main.py                # Main bootstrap script
│   ├── core/                  # Configurations, constants & models
│   ├── gui/                   # CustomTkinter widgets & view panels
│   ├── controllers/           # UI State handlers & event routers
│   ├── services/              # Pure domain logic coordinates
│   └── utils/                 # Multi-threading managers
├── tests/                     # Test suites (PyTest conftests)
├── pyproject.toml             # Ruff, Black, mypy, pytest configs
├── requirements.txt           # Master runtime dependencies installer
```

---

## 🚀 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/CoderDebajyoti/Attendence-System-Uning-Face-Recognition.git
cd Attendence-System-Uning-Face-Recognition
```

### 2. Configure Virtual Environment
```bash
python -m venv .venv
# Activate on Windows:
.venv\Scripts\activate
# Activate on Unix/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create local environment configuration
Copy the template `.env.example` to `.env`:
```bash
copy .env.example .env
```
Ensure you change the `SECRET_KEY` value in production settings.

---

## 💻 Running the Application

Start the system by launching the bootstrap script:
```bash
python src/main.py
```

### First-Run Setup Flow
1. If no administrator user is found in the database on launch, the application displays the **System Setup Wizard**.
2. Input a secure username and password (minimum 6 characters) to register the initial administrator.
3. Log in using your new credentials.
4. Navigate to **Students** to register a student profile.
5. Open the **Dataset** tab, select the student, start the camera, and capture at least 25 template frames (ensure proper lighting and centering).
6. Open **Recognition**, click **Build Model** (trains the LBPH Face Recognizer), then click **Start Camera** and toggle **Face Recognition ON** to check in students automatically.
7. Navigate to **Reports** to preview metrics or export files.
8. Edit parameters on the **Settings** page and click **Save Configurations** (you can click **Test Camera Stream Feed** to check index connections).
9. Click **Logout** to lock access.

---

## 🧪 Automated Testing

Run the test suite using `pytest`:
```bash
# Run tests inside the virtual environment
.venv\Scripts\python -m pytest
```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
