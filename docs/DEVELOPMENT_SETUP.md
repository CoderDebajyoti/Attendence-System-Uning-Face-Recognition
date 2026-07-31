# Face Recognition Attendance System - Development Setup Guide

This document guides developers through setting up their workspace, configuring dependencies, and preparing directories for coding.

---

## 1. Prerequisites

Before starting, ensure your machine meets the following environment targets:
- **Python**: Version 3.12+ (Verify using `python --version` or `python3 --version`).
- **Git**: Installed and configured.
- **Operating System**: Windows (Primary compiled target), macOS, or Linux.
- **Compiler Accessories (Windows only)**: C++ Build Tools (required for some dependency builds such as `insightface` compilation).

---

## 2. Directory Scaffolding

To separate execution files from operational footprints, the project uses dedicated, git-ignored folders:

| Directory Path | Role | Lifecycle |
| :--- | :--- | :--- |
| `database/` | Primary data folder. SQLite file is placed here. | Persistent locally. |
| `database/backups/` | Storage for rotational sqlite backups. | Managed by backup utilities. |
| `database/exports/` | Generated attendance report files (Excel, PDF). | Ephemeral. |
| `database/datasets/` | Enrolled aligned crops ($112 \times 112$ pixels) categorized by ID. | Biometric directory. |
| `logs/` | System diagnostic outputs and audit trails. | Rotated daily. |
| `models/` | ArcFace and RetinaFace model checkpoints (.onnx). | Read-only imports. |

---

## 3. Sandboxed Setup Instructions

### 3.1 Windows Setup (Standard)
Run the automated environment setup wizard from your command line:
```cmd
scripts\setup_env.bat
```
This automatically handles virtual environment creation, pip upgrades, directory formations, and copying `.env.example` to `.env`.

### 3.2 macOS & Linux Setup
Run the automated shell setup wizard:
```bash
chmod +x scripts/setup_env.sh
./scripts/setup_env.sh
```

---

## 4. Configuration Tuning

1. Copy the `.env.example` template at the root directory and rename it to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and adjust the local values:
   - `CAMERA_ID`: Set to `0` for default webcam, or provide a network link string in `CAMERA_RTSP_URL`.
   - `RECOGNITION_THRESHOLD`: Start at the recommended default (`0.65`).
   - `DATABASE_URL`: Defaults to local SQLite. Swap to PostgreSQL if staging tests require it.

---

## 5. Development Tools Execution

The virtual environment includes formatters, linters, and type checkers configured via `pyproject.toml`. Run these checkers from the active environment terminal:

### Formatter (Black)
```bash
black src/ tests/
```

### Linter (Ruff)
```bash
ruff check src/ tests/
```

### Static Type Checker (mypy)
```bash
mypy src/
```

### Test Runner (pytest)
```bash
pytest tests/
```
Alternatively, developers using Bash/WSL can execute standard command shorthands: `make format`, `make lint`, `make type`, `make test`.
