# Face Recognition Attendance System - Contributing Guide

First of all, thank you for considering contributing to the Face Recognition Attendance System! As a portfolio project built to professional standards, your input is highly valued.

---

## 1. Code of Conduct

We prioritize a respectful, welcoming, and professional environment. Please ensure all interactions in issues, pull requests, and discussions remain polite, constructive, and supportive of all community levels.

---

## 2. How to Contribute

### 2.1 Reporting Bugs
1. Before submitting a bug, search active Issues to see if the problem has already been reported.
2. If new, open a Bug Report using our [Bug Report Template](file:///.github/ISSUE_TEMPLATE/bug_report.md).
3. Provide details on how to reproduce the issue, and attach logs from `logs/app_system.log`.

### 2.2 Proposing Enhancements
1. Open a Feature Request using our [Feature Request Template](file:///.github/ISSUE_TEMPLATE/feature_request.md).
2. Describe the feature, show how it adds value to the system, and propose visual layouts if applicable.

### 2.3 Submitting Pull Requests (PRs)
1. Fork the repository and create your topic branch from `main`:
   ```bash
   git checkout -b feat/my-cool-feature
   ```
2. Follow our [Development Setup Guide](file:///c:/GitHub/Attendence-System-Uning-Face-Recognition/docs/DEVELOPMENT_SETUP.md) to initialize your workspace.
3. Keep code modifications focused on a single concern.
4. Format and lint your changes:
   ```bash
   black src/ tests/
   ruff check src/ tests/
   mypy src/
   ```
5. Ensure all unit and integration tests run successfully:
   ```bash
   pytest tests/
   ```
6. Commit your changes using Conventional Commit patterns.
7. Push the topic branch to your fork and submit a PR to our `main` branch.

---

## 3. Pull Request Review Process

- **Automated Checkers**: GitHub Actions run formatters, linters, and testing suites. PRs with failing steps will not be merged.
- **Peer Review**: A project maintainer will review code structures, verification coverage, and documentation consistency before approval.
- **Squash and Merge**: Commits are squashed on merge to keep the core git log concise.
