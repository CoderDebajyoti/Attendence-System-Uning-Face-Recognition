# ==============================================================================
# Face Recognition Attendance System - Development Automation Makefile
# ==============================================================================

.PHONY: setup install format lint type test clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup   - Create virtual environment and directory hooks"
	@echo "  make install - Install runtime and development dependencies"
	@echo "  make format  - Format code using Black"
	@echo "  make lint    - Lint code using Ruff"
	@echo "  make type    - Run static type checking using mypy"
	@echo "  make test    - Run test suites using pytest"
	@echo "  make clean   - Clean cache directories and logs"

setup:
	@echo "Creating sandbox structures..."
	python -m venv .venv
	@echo "Virtual environment created. Run 'source .venv/bin/activate' or '.venv\\Scripts\\activate'"
	mkdir -p database logs models database/backups database/exports database/datasets

install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements/dev.txt -r requirements/testing.txt

format:
	@echo "Formatting codebase..."
	black src/ tests/

lint:
	@echo "Linting codebase..."
	ruff check src/ tests/

type:
	@echo "Type checking codebase..."
	mypy src/

test:
	@echo "Running tests..."
	pytest --cov=src tests/

clean:
	@echo "Cleaning caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist build
	@echo "Caches cleaned."
