# Face Recognition Attendance System - Database Design

This document details the relational database schema designed for the Face Recognition Attendance System. The schema supports strict data integrity, historical auditing, and scales transparently from a local **SQLite** database during development to an enterprise **PostgreSQL** deployment in production.

---

## 1. Entity Relationship (ER) Diagram
The database schema utilizes standard relational constraints. Below is the ER Diagram defining the relationships between core tables:

```mermaid
erDiagram
    DEPARTMENTS ||--o{ COURSES : "contains"
    DEPARTMENTS ||--o{ FACULTY : "employs"
    COURSES ||--o{ STUDENTS : "enrolls"
    COURSES ||--o{ SUBJECTS : "teaches"
    FACULTY ||--o{ SUBJECTS : "teaches"
    
    USERS }|--|| ROLES : "has"
    ROLES ||--o{ ROLE_PERMISSIONS : "defines"
    PERMISSIONS ||--o{ ROLE_PERMISSIONS : "assigned_to"
    USERS ||--o| FACULTY : "links_to"

    STUDENTS ||--o{ FACE_EMBEDDINGS : "has"
    STUDENTS ||--o{ ATTENDANCE : "marked_for"
    STUDENTS ||--o{ ATTENDANCE_LOGS : "triggered"
    SUBJECTS ||--o{ ATTENDANCE : "logged_under"
    USERS ||--o{ ATTENDANCE : "marked_by"

    DEPARTMENTS {
        int id PK
        string name
        string code UNIQUE
    }

    COURSES {
        int id PK
        string name
        string code UNIQUE
        int department_id FK
    }

    SUBJECTS {
        int id PK
        string name
        string code UNIQUE
        int course_id FK
        int faculty_id FK
    }

    ROLES {
        int id PK
        string name UNIQUE
        string description
    }

    PERMISSIONS {
        int id PK
        string name UNIQUE
        string description
    }

    ROLE_PERMISSIONS {
        int role_id PK, FK
        int permission_id PK, FK
    }

    USERS {
        int id PK
        string username UNIQUE
        string password_hash
        string email UNIQUE
        int role_id FK
        boolean is_active
    }

    FACULTY {
        int id PK
        int user_id FK
        string employee_code UNIQUE
        string first_name
        string last_name
        int department_id FK
    }

    STUDENTS {
        int id PK
        string student_code UNIQUE
        string first_name
        string last_name
        int department_id FK
        int course_id FK
        boolean is_active
    }

    FACE_EMBEDDINGS {
        int id PK
        int student_id FK
        blob embedding_blob
        string file_path
        datetime created_at
    }

    ATTENDANCE {
        int id PK
        int student_id FK
        int subject_id FK
        date date
        time time_in
        string status
        int marked_by_user_id FK
    }

    ATTENDANCE_LOGS {
        int id PK
        int student_id FK
        float similarity_score
        int matched_embedding_id FK
        datetime timestamp
        string image_path
        string status
    }
```

---

## 2. Table Specifications

### 2.1 departments
Stores academic or organizational departments.
- **Indexes**: Unique index on `code`.
- **Relationships**: One-to-many with `courses` and `faculty`.

| Column | Data Type (SQLite) | Data Type (PG) | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | SERIAL | PRIMARY KEY, AUTOINCREMENT | Internal department ID. |
| `name` | VARCHAR(100) | VARCHAR(100) | NOT NULL | Department Name (e.g., Computer Science). |
| `code` | VARCHAR(10) | VARCHAR(10) | UNIQUE, NOT NULL | Code acronym (e.g., CSE). |

### 2.2 courses
Academic degree plans or curriculum divisions.
- **Indexes**: Unique index on `code`.
- **Relationships**: Belongs to `departments`. One-to-many with `students`, `subjects`.

| Column | Data Type (SQLite) | Data Type (PG) | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | SERIAL | PRIMARY KEY | Internal course ID. |
| `name` | VARCHAR(100) | VARCHAR(100) | NOT NULL | Course Name (e.g., Bachelor of Technology). |
| `code` | VARCHAR(20) | VARCHAR(20) | UNIQUE, NOT NULL | Course code (e.g., BTECH-CSE). |
| `department_id` | INTEGER | INTEGER | FOREIGN KEY, NOT NULL | References `departments(id)` ON DELETE RESTRICT. |

### 2.3 subjects
Specific study items taught by faculty members.
- **Relationships**: Belongs to `courses` and `faculty`. One-to-many with `attendance`.

| Column | Data Type (SQLite) | Data Type (PG) | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | SERIAL | PRIMARY KEY | Internal subject ID. |
| `name` | VARCHAR(100) | VARCHAR(100) | NOT NULL | Subject name (e.g., Operating Systems). |
| `code` | VARCHAR(20) | VARCHAR(20) | UNIQUE, NOT NULL | Subject code (e.g., CS-401). |
| `course_id` | INTEGER | INTEGER | FOREIGN KEY, NOT NULL | References `courses(id)` ON DELETE CASCADE. |
| `faculty_id` | INTEGER | INTEGER | FOREIGN KEY, NULL | References `faculty(id)` ON DELETE SET NULL. |

### 2.4 roles & permissions
User authorization configuration.
- **`role_permissions`** represents the junction table resolving the many-to-many mapping.

#### `roles`
| Column | Data Type (SQLite) | Data Type (PG) | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | SERIAL | PRIMARY KEY | Primary Key. |
| `name` | VARCHAR(50) | VARCHAR(50) | UNIQUE, NOT NULL | Role descriptor (e.g., Admin, Faculty). |
| `description` | TEXT | TEXT | NULL | Context notes. |

#### `permissions`
| Column | Data Type (SQLite) | Data Type (PG) | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | SERIAL | PRIMARY KEY | Primary Key. |
| `name` | VARCHAR(50) | VARCHAR(50) | UNIQUE, NOT NULL | Action key (e.g., `student:create`, `settings:write`). |
| `description` | TEXT | TEXT | NULL | Details. |

#### `role_permissions`
- **Constraints**: Composite Primary Key `(role_id, permission_id)`.

| Column | Data Type (SQLite) | Data Type (PG) | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `role_id` | INTEGER | INTEGER | FK, NOT NULL | References `roles(id)` ON DELETE CASCADE. |
| `permission_id` | INTEGER | INTEGER | FK, NOT NULL | References `permissions(id)` ON DELETE CASCADE. |

### 2.5 users
Handles credentials for system access.
- **Indexes**: Unique index on `username`, `email`.

| Column | Data Type (SQLite) | Data Type (PG) | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | SERIAL | PRIMARY KEY | Internal User ID. |
| `username` | VARCHAR(50) | VARCHAR(50) | UNIQUE, NOT NULL | Unique login handle. |
| `password_hash` | VARCHAR(255) | VARCHAR(255) | NOT NULL | Salted hashing string (e.g., bcrypt). |
| `email` | VARCHAR(100) | VARCHAR(100) | UNIQUE, NOT NULL | Contact email. |
| `role_id` | INTEGER | INTEGER | FOREIGN KEY, NOT NULL | References `roles(id)` ON DELETE RESTRICT. |
| `is_active` | BOOLEAN | BOOLEAN | DEFAULT TRUE | System login permission switch. |

### 2.6 faculty
Details for teaching or managing staff.
- **Indexes**: Unique index on `employee_code`.

| Column | Data Type (SQLite) | Data Type (PG) | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | SERIAL | PRIMARY KEY | Internal Faculty ID. |
| `user_id` | INTEGER | INTEGER | FOREIGN KEY, UNIQUE, NULL | References `users(id)` ON DELETE SET NULL. |
| `employee_code` | VARCHAR(50) | VARCHAR(50) | UNIQUE, NOT NULL | Organization ID. |
| `first_name` | VARCHAR(50) | VARCHAR(50) | NOT NULL | First Name. |
| `last_name` | VARCHAR(50) | VARCHAR(50) | NOT NULL | Last Name. |
| `department_id` | INTEGER | INTEGER | FOREIGN KEY, NOT NULL | References `departments(id)`. |

### 2.7 students
Biometrically tracked individuals.
- **Indexes**: Unique index on `student_code`. Index on `course_id`.

| Column | Data Type (SQLite) | Data Type (PG) | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | SERIAL | PRIMARY KEY | Internal Student ID. |
| `student_code` | VARCHAR(50) | VARCHAR(50) | UNIQUE, NOT NULL | Student registration code (e.g., STD2026001). |
| `first_name` | VARCHAR(50) | VARCHAR(50) | NOT NULL | First name. |
| `last_name` | VARCHAR(50) | VARCHAR(50) | NOT NULL | Last name. |
| `department_id` | INTEGER | INTEGER | FOREIGN KEY, NOT NULL | References `departments(id)`. |
| `course_id` | INTEGER | INTEGER | FOREIGN KEY, NOT NULL | References `courses(id)`. |
| `is_active` | BOOLEAN | BOOLEAN | DEFAULT TRUE | Active search loop filter. |

### 2.8 face_embeddings
Biometric vectors mapping to students. One student can have multiple embedding variations (multi-sample registration).
- **Indexes**: Index on `student_id`.
- **Note**: The vector is extracted as an array of 512 floats and stored as a binary serialization array (Python `pickle` or NumPy byte stream representation).

| Column | Data Type (SQLite) | Data Type (PG) | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | SERIAL | PRIMARY KEY | Primary key. |
| `student_id` | INTEGER | INTEGER | FOREIGN KEY, NOT NULL | References `students(id)` ON DELETE CASCADE. |
| `embedding_blob` | BLOB | BYTEA | NOT NULL | Binary container for 512-dimensional vector. |
| `file_path` | VARCHAR(255) | VARCHAR(255) | NOT NULL | Link to physical crop image on disk. |
| `created_at` | DATETIME | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date of enrollment. |

### 2.9 attendance
Core attendance records mapped to courses and sessions.
- **Indexes**: Composite Index on `(student_id, subject_id, date)` to quickly prevent duplicates and fetch histories.

| Column | Data Type (SQLite) | Data Type (PG) | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | SERIAL | PRIMARY KEY | Primary key. |
| `student_id` | INTEGER | INTEGER | FOREIGN KEY, NOT NULL | References `students(id)` ON DELETE CASCADE. |
| `subject_id` | INTEGER | INTEGER | FOREIGN KEY, NOT NULL | References `subjects(id)` ON DELETE CASCADE. |
| `date` | DATE | DATE | NOT NULL | Date of session. |
| `time_in` | TIME | TIME | NOT NULL | Stamp when target was recognized. |
| `status` | VARCHAR(20) | VARCHAR(20) | NOT NULL | Status (Present, Absent, Late, Excused). |
| `marked_by_user_id` | INTEGER | INTEGER | FOREIGN KEY, NULL | References `users(id)` (null if fully auto). |

### 2.10 attendance_logs
A system audit trail of individual recognition attempts. Includes unknown faces and match scoring configurations for fine-tuning.
- **Indexes**: Index on `student_id`, Index on `timestamp`.

| Column | Data Type (SQLite) | Data Type (PG) | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | SERIAL | PRIMARY KEY | Primary key. |
| `student_id` | INTEGER | INTEGER | FOREIGN KEY, NULL | References `students(id)` ON DELETE CASCADE (null if unknown). |
| `similarity_score` | REAL | DOUBLE PRECISION | NOT NULL | Match confidence calculated. |
| `matched_embedding_id` | INTEGER | INTEGER | FOREIGN KEY, NULL | References `face_embeddings(id)`. |
| `timestamp` | DATETIME | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Execution timestamp. |
| `image_path` | VARCHAR(255) | VARCHAR(255) | NULL | Path to the captured verification crop frame. |
| `status` | VARCHAR(50) | VARCHAR(50) | NOT NULL | Match status outcome (e.g., Success, BelowThreshold). |

---

## 3. Normalization & Optimization Analysis

### 3.1 Normalization State (Third Normal Form - 3NF)
- **First Normal Form (1NF)**: Every table has a primary key, and all cells contain single, atomic values. Biometric embeddings are single arrays mapped as a blob cell, treated as a single compound attribute.
- **Second Normal Form (2NF)**: All non-key attributes are fully functionally dependent on the entire primary key. Junction tables (like `role_permissions`) use joint keys and contain only relation mappings.
- **Third Normal Form (3NF)**: Transitive dependencies are removed. Student course allocations are linked via `course_id`, pointing directly to the courses catalog. Subject and faculty linkages are separated from student logs.

### 3.2 Performance Indexes
1. **Attendance Fast Lookups**: `idx_attendance_lookup` on `(subject_id, date, student_id)` allows reporting queries to scan matching records in logarithmic time.
2. **Student Identity Matching**: Unique index on `students(student_code)` guarantees zero code collision.
3. **Face Embedding Scanning**: `idx_embedding_student` on `face_embeddings(student_id)` supports quick cleanups during student dataset deletions or re-training.
