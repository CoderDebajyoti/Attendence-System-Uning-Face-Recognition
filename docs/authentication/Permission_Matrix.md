# Permission Matrix Specification

This document details the granular permission permissions mapped to each user role within the **Face Recognition Attendance System**.

---

## 1. Mapped Permissions Matrix

The table below maps the operations to the role entities. In compliance with the **Least Privilege Principle**, roles inherit only the required scopes.

| Functional Area | Scope Permission Key | Super Admin | Administrator | Faculty | Lab Assistant | Student (Future) | Viewer (Future) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **System Settings** | `settings:read` | ✓ | ✓ | | | | |
| | `settings:write` | ✓ | | | | | |
| **User Accounts** | `user:create` | ✓ | ✓ | | | | |
| | `user:read` | ✓ | ✓ | | | | |
| | `user:update` | ✓ | ✓ | | | | |
| | `user:delete` | ✓ | | | | | |
| **Faculty Records** | `faculty:create` | ✓ | ✓ | | | | |
| | `faculty:read` | ✓ | ✓ | ✓ | | | |
| | `faculty:update` | ✓ | ✓ | | | | |
| | `faculty:delete` | ✓ | | | | | |
| **Student Roster** | `student:create` | ✓ | ✓ | ✓ | | | |
| | `student:read` | ✓ | ✓ | ✓ | ✓ | | ✓ |
| | `student:update` | ✓ | ✓ | ✓ | | | |
| | `student:delete` | ✓ | | | | | |
| **Academic Courses**| `course:create` | ✓ | ✓ | | | | |
| | `course:read` | ✓ | ✓ | ✓ | ✓ | | ✓ |
| | `course:update` | ✓ | ✓ | | | | |
| | `course:delete` | ✓ | | | | | |
| **Biometric Datasets**| `dataset:capture` | ✓ | ✓ | ✓ | | | |
| | `dataset:delete` | ✓ | ✓ | | | | |
| **AI Inference Engines**| `model:evaluate` | ✓ | ✓ | ✓ | ✓ | | |
| | `model:update` | ✓ | | | | | |
| **Attendance Records**| `attendance:create`| ✓ | ✓ | ✓ | ✓ | | |
| | `attendance:read` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| | `attendance:update`| ✓ | ✓ | ✓ | ✓ | | |
| | `attendance:delete`| ✓ | | | | | |
| **Analytics Reporting**| `reports:export` | ✓ | ✓ | ✓ | | | ✓ |
| **Database Operations**| `database:backup` | ✓ | | | | | |
| | `database:restore`| ✓ | | | | | |
| **Audit Logs** | `logs:view` | ✓ | | | | | |
| | `logs:clear` | ✓ | | | | | |

---

## 2. Scope & Key Naming Conventions

Granular keys follow a standardized `<resource>:<action>` format to ensure simple mapping:

*   **`<resource>`**: Represents the target entity or domain boundary (e.g. `student`, `attendance`, `settings`, `dataset`).
*   **`<action>`**: Maps to standard access classifications:
    *   `read`: View records or access monitoring dashboards.
    *   `create`: Insert new records or register configurations.
    *   `update`: Modify existing records or credentials.
    *   `delete`: Remove entities or mark them inactive.
    *   `export`: Package and download file structures.
    *   `backup` / `restore` / `clear`: Administrative infrastructure controls.
