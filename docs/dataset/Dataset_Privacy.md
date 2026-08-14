# Biometric Dataset Privacy & Security

This document outlines the privacy-conscious design patterns and data security controls implemented for managing sensitive biometric data.

---

## Biometric Data Sensitivity

Facial images and embeddings are personal identifiers and are subject to strict privacy regulations (e.g. GDPR, CCPA). The system is designed to handle these datasets securely.

---

## Technical Security Controls

### 1. File Access Controls
*   Datasets are stored inside a dedicated local subfolder (`database/datasets`).
*   Directory permissions should restrict access to the system owner or runtime user.

### 2. Version Control Exclusion (Git)
*   The `.gitignore` file strictly blocks the `database/datasets/` folder, ensuring no personal images are pushed to remote repositories.

### 3. Log Protection
*   The system logger (`app.recognition`) does not print raw pixel arrays, image hashes, or file contents.
*   Only high-level status messages (e.g., "Face detected. Image captured.") are logged to prevent leaking biometric info.

### 4. Database Security
*   The SQLite file is stored locally in `database/app_database.db` and is not exposed to external networks.
*   We do not store plain-text personal identifiers alongside dataset crops.
