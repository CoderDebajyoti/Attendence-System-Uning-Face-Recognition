# Security Policies Specification

This document details the core security principles, development guidelines, and configuration policies enforced in the **Face Recognition Attendance System**.

---

## 1. Core Security Principles

### 1.1 Least Privilege Principle
*   **Default Deny**: By default, any operation is locked. Permission checks require explicit mapping in the active session configuration.
*   **Interface Reduction**: GUI views are dynamically generated based on permissions. Users are not shown administrative tools or menus if their roles do not contain the matching permission scopes.

### 1.2 Defense in Depth
*   Security controls are layered across three boundaries to guarantee access limits even if one layer is compromised:
    1.  **GUI Boundary**: CustomTkinter buttons are disabled, and unauthorized navigation items are hidden from the sidebar menu.
    2.  **Service Layer Boundary**: Decorators intercept service method entries to verify permission scopes in the memory context.
    3.  **Database Boundary**: Repository queries validate foreign key constraints and utilize parameter binding.

### 1.3 Separation of Duties
*   Responsibilities are strictly divided across roles to prevent single-point failures:
    *   **Faculty** can register students and manage local attendance records but cannot provision user accounts.
    *   **Administrators** can provision user accounts and departments but cannot modify database file paths, override recognition confidence thresholds, or clear logs.
    *   **Super Admins** can manage database files and configurations but do not participate in day-to-day attendance tracking.

### 1.4 Secure Defaults
*   Newly provisioned user accounts are configured with `force_password_change = True`.
*   System settings default to the most conservative security values (e.g. strict confidence threshold = `0.65`, logging level = `INFO`).

---

## 2. Input Validation & Error Handling Policies

### 2.1 Input Sanitization
*   All strings entered into the GUI forms are sanitized before processing using regex pattern verification to block injection vectors:
    *   Names/Texts: `^[a-zA-Z\s.-]{2,50}$`
    *   Email: Standard RFC 5322 compliance pattern.
    *   System IDs/Codes: `^[a-zA-Z0-9-]{3,20}$`

### 2.2 Error Message Obfuscation (Timing & Enumeration Mitigation)
*   **Authentication Failures**: The system returns a generic message: *"Invalid username or password"* for both non-existent usernames and incorrect passwords.
*   **Detail Leakage**: Stack traces and file paths are never written to the GUI error labels. In production, errors are captured under an localized code (e.g., `ERR-501`) and written to the secure log file (`app_system.log`) while the user is shown a simple warning panel.

---

## 3. Secret & Configuration Management

*   **Dotenv Pattern**: Environment-specific variables (database credentials, local RTSP paths, cryptography secret keys) are kept in a local `.env` file that is listed in `.gitignore` to prevent commits to repository history.
*   **File Permissions**: On startup, the launcher verifies that local settings files (`.env`, database backups) are set to read/write only by the operating system account running the desktop process.
