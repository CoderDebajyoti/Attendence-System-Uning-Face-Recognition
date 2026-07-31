@echo off
:: ==============================================================================
:: Face Recognition Attendance System - Windows Environment Setup Wizard
:: ==============================================================================
echo ==========================================================
echo Starting Face Recognition Attendance System Workspace Setup...
echo ==========================================================

:: 1. Verify Python Installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your system PATH.
    echo Please install Python 3.12+ and try again.
    pause
    exit /b 1
)

:: 2. Create Virtual Environment if missing
if not exist ".venv" (
    echo Creating virtual environment (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo Virtual environment (.venv) already exists. Skipping creation.
)

:: 3. Create Sandbox Folder Structures
echo Initializing database, log, and AI model folders...
if not exist "database" mkdir database
if not exist "logs" mkdir logs
if not exist "models" mkdir models
if not exist "database\backups" mkdir database\backups
if not exist "database\exports" mkdir database\exports
if not exist "database\datasets" mkdir database\datasets
echo Directory structures initialized.

:: 4. Copy .env.example if local .env does not exist
if not exist ".env" (
    echo Copying .env.example to active .env config...
    copy .env.example .env >nul
    echo Initialized local .env configuration override.
) else (
    echo Active .env file already exists. Skipping template overwrite.
)

:: 5. Activate Environment and Install Requirements
echo Activating virtual environment and upgrading pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip

echo Installing dependencies (this may take a moment)...
pip install -r requirements.txt
pip install -r requirements/dev.txt -r requirements/testing.txt

if %errorlevel% neq 0 (
    echo [WARNING] Dependency installation encountered warning flags.
    echo Please verify package list.
) else (
    echo Packages installed successfully.
)

echo ==========================================================
echo Setup complete! To start developing:
echo   1. Run: .venv\Scripts\activate
echo   2. Run: python src/main.py
echo ==========================================================
pause
