# Face Recognition Attendance System - Security Planning

This document details the security design and data privacy guidelines for the Face Recognition Attendance System. Since this system processes sensitive biometric data, security is built into the architecture.

---

## 1. Security Architecture Diagram
Below is the security boundary diagram representing data classification and encryption boundaries:

```mermaid
flowchart TD
    Camera[USB / RTSP Camera Feed] -->|Raw Visual Data: Ephemeral| OS_CAM[OS Camera Permission Layer]
    OS_CAM -->|Authorized Stream| PyEngine[Face Recognition Engine]
    
    subgraph Secure_Boundary [Local App Sandbox]
        PyEngine -->|Extract Embeddings| Memory[RAM Vector Array]
        Memory -->|512 Float Vector| Encrypter[Data Access Layer]
        Encrypter -->|Write Hash/Vector| SQLite[(SQLite DB)]
        
        Config[config.yaml] -->|Environment Override| DecryptConf[Decrypted in Memory]
    end
    
    Faculty[Faculty Panel] -->|Plaintext Password| Hashing[bcrypt Hashing Engine]
    Hashing -->|Salted Hash| SQLite
    
    classDef secure fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef clear fill:#ffebee,stroke:#c62828,stroke-width:1px;
    class Secure_Boundary secure;
    class Camera,Config clear;
```

---

## 2. Core Security Protocols

### 2.1 Password Hashing & Authentication
- **Protocol**: Faculty and admin credentials are never stored in plaintext. Passwords are salted and hashed using **bcrypt** (or **Argon2id**).
- **Verification**: During login, the password input is compared against the database hash using the library’s native constant-time matching function (`bcrypt.checkpw()`), preventing timing attacks.
- **Session Management**: Session tokens are maintained purely in local RAM memory during runtime; logging out destroys the session object immediately.

### 2.2 Biometric Data Protection & GDPR Compliance
Biometric vectors (embeddings) are highly sensitive. We enforce the following safety rules:
1. **No Original Image Retention (Configurable)**: Once the enrollment wizard successfully aligns a face and generates the 512-dimensional vector, the original high-resolution enrollment photos can be deleted from disk (based on organization privacy policy), keeping only the mathematical representation (the embedding). It is virtually impossible to reconstruct a human face from a 512-d float embedding.
2. **Encrypted Storage**: On production networks (PostgreSQL), connections must utilize TLS/SSL encryption to prevent sniffing of embeddings. On local SQLite, database file permissions are set to read/write only by the system user running the process.

### 2.3 SQL Injection Prevention
- **SQLAlchemy ORM**: Raw SQL concatenations (e.g., `f"SELECT * FROM students WHERE name = '{input}'"`) are strictly prohibited.
- **Parameter Binding**: All queries use SQLAlchemy's built-in parameter binding and type checking:
  ```python
  # Safe Implementation
  session.query(Student).filter(Student.student_code == student_code).first()
  ```
  This ensures that user input is treated as literal values rather than executable code.

### 2.4 Input Validation & Sanitization
- **Strict RegEx Filtering**: All textual user input (e.g., name, student code) is sanitized before database submission to prevent Cross-Site Scripting (XSS) equivalents in logs and path traversals in file exports.
  - Names: `^[a-zA-Z\s.-]{2,50}$`
  - Codes: `^[a-zA-Z0-9-]{3,20}$`
- **Type Safety**: Pydantic schemas or Python dataclasses are used at the service layer boundaries to validate structure types.

### 2.5 Camera Permissions & Feed Integrity
- **OS Permission Hooks**: On startup, the camera helper probes the target camera. On Windows, it handles direct Media Foundation hooks. On macOS/Linux, it catches system exceptions if camera permission is denied and displays an instructional message inside the GUI canvas instead of crashing.
- **RTSP Credentials**: For network IP cameras, RTSP URLs containing credentials (e.g., `rtsp://admin:password@192.168.1.100:554/stream`) must not be stored in plaintext. They are encrypted in `config.yaml` using a local environment machine key (such as cryptography’s `Fernet` symmetric encryption utilizing the Windows DPAPI wrapper).

### 2.6 Role-Based Access Control (RBAC)
Authorizations are enforced at the service layer. Every view execution is validated:

| Role | Permissions | Access Restrictions |
| :--- | :--- | :--- |
| **System Admin** | Global access: DB configs, system logging views, user registration, backups. | None. |
| **Faculty** | Course registry, student registrations, dataset generation, view attendance, report export. | Cannot modify database paths, adjust model thresholds, create user accounts, or read system debug logs. |
| **Student** | Biometric verification only. | Zero access to the GUI dashboard. |

---

## 3. Database Backup & Disaster Recovery
- **Backup Routine**: Every 24 hours (or on application exit), the system copies the SQLite database file to a `backups/` directory using an asynchronous copy process:
  ```python
  # SQLite safe backup sequence
  import sqlite3
  con = sqlite3.connect('data/app_database.db')
  bck = sqlite3.connect('data/backups/app_database_backup.db')
  with bck:
      con.backup(bck)
  ```
- **PG Backups**: For PostgreSQL deployments, the system configuration guides administrators to schedule standard `pg_dump` cron jobs.
