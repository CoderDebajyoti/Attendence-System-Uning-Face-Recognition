#!/bin/bash
# ==============================================================================
# Face Recognition Attendance System - Unix Environment Setup Wizard
# ==============================================================================
set -e # Terminate immediately on error

echo "=========================================================="
echo "Starting Face Recognition Attendance System Workspace Setup..."
echo "=========================================================="

# 1. Verify Python Installation
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in system PATH."
    exit 1
fi

# 2. Create Virtual Environment if missing
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment (.venv)..."
    python3 -m venv .venv
    echo "Virtual environment created successfully."
else
    echo "Virtual environment (.venv) already exists. Skipping creation."
fi

# 3. Create Sandbox Folder Structures
echo "Initializing database, log, and AI model folders..."
mkdir -p database logs models database/backups database/exports database/datasets
echo "Directory structures initialized."

# 4. Copy .env.example if local .env does not exist
if [ ! -f ".env" ]; then
    echo "Copying .env.example to active .env config..."
    cp .env.example .env
    echo "Initialized local .env configuration override."
else
    echo "Active .env file already exists. Skipping template overwrite."
fi

# 5. Activate Environment and Install Requirements
echo "Activating virtual environment and upgrading pip..."
source .venv/bin/activate
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements/dev.txt -r requirements/testing.txt

echo "=========================================================="
echo "Setup complete! To start developing:"
echo "  1. Run: source .venv/bin/activate"
echo "  2. Run: python src/main.py"
echo "=========================================================="
