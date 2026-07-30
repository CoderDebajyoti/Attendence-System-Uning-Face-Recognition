# Face Recognition Attendance System - Deployment Plan

This document details the configuration and packaging roadmap for deploying the Face Recognition Attendance System to development, staging, and client environments.

---

## 1. Environments

The application operates across three runtime environments:

| Feature / Detail | Development | Staging / QA | Production |
| :--- | :--- | :--- | :--- |
| **Database** | SQLite (local `app_database.db`) | SQLite (populated with dummy datasets) | SQLite (single terminal) or PostgreSQL (multi-terminal network) |
| **Camera Interface** | Local laptop webcam (Index 0) | USB webcam or virtual test video loop | Fixed ceiling-mounted IP Camera (RTSP stream) |
| **Hardware Target** | CPU-only execution | CPU-only testing | Core i5+ CPU or NVIDIA Jetson Nano/GeForce GPU (CUDA enabled) |
| **Installation Code**| Source code (`python src/main.py`) | Source / packaged zip folders | Standalone Compiled Executable (.exe / binary) |

---

## 2. Desktop Packaging Strategy (PyInstaller)

To deploy the application to machines without requiring Python runtimes or library installations, the project is compiled into a standalone folder/executable using **PyInstaller**.

### 2.1 ONNX & CustomTkinter Asset Constraints
PyInstaller often misses non-code asset files and third-party binaries (such as ONNX Runtime dynamic link libraries `.dll` / `.so`, and CustomTkinter theme files). We resolve this using explicit configuration in a PyInstaller SPEC file (`app.spec`):

```python
# Simplified app.spec configuration layout reference
import sys
import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collect CustomTkinter theme assets
customtkinter_data = collect_data_files('customtkinter')

added_files = [
    ('src/ui/assets', 'ui/assets'),
    ('config/config.default.yaml', 'config'),
    ('config/logging.config.json', 'config')
] + customtkinter_data

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[], # System specific ONNX runtime DLLs are placed here if missed
    datas=added_files,
    hiddenimports=[
        'sqlalchemy.ext.declarative',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.dialects.postgresql'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FaceRecognitionAttendance',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True, # Compress binaries using UPX
    console=False, # Disable console popup window in production
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/ui/assets/icons/app_logo.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FaceRecognitionAttendanceSystem',
)
```

### 2.2 Compilation Command
For Windows compilation, developers execute:
```powershell
pyinstaller --clean --noconfirm app.spec
```
This generates a distributable `dist/FaceRecognitionAttendanceSystem/` directory containing all DLL dependencies, models, assets, and the primary executable.

---

## 3. Database Migrations (Alembic)

As schemas evolve (e.g., adding liveness scores to log tables), database updates must be managed safely without erasing historical attendance records.
- **Tool**: We utilize **Alembic** (SQLAlchemy’s migration framework).
- **Migration Protocol**:
  1. Initialize Alembic: `alembic init src/data_access/migrations`
  2. Generate migration scripts: `alembic revision --autogenerate -m "Add new column"`
  3. Deploy migrations to target SQLite or PostgreSQL instances: `alembic upgrade head`
- **Backup Before Migration**: The migration runner script triggers the SQLite backup sequence automatically before executing any schema modifications.

---

## 4. Hardware Installation Best Practices
For production face recognition tracking in corporate offices or school entryways:
- **Mounting Height**: Camera should be mounted at a height of $1.6 - 1.8\text{ meters}$ pointing slightly down.
- **Lighting Control**: Avoid placing the camera facing direct exterior windows (strong backlighting). Install low-cost LED diffuser lamps above the checkpoint area to ensure constant facial lighting.
- **Network Pipeline**: For IP RTSP cameras, connect both the capture PC and camera via physical Gigabit Ethernet cords rather than Wi-Fi to prevent frame drops and network latency spikes.
