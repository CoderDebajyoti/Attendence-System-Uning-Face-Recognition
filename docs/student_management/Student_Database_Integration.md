# Database Integration & Seeding Workflow

This document explains the database initialization, SQLite pragma settings, and the startup seeding mechanism.

---

## 1. Connection Configurations

The application initializes its database connection during bootstrapping in `src/main.py`:

- **Path Resolution**: The SQLite file path is parsed from `settings.database_url`. If it is a local path (e.g. `sqlite:///database/app_database.db`), the system automatically creates the parent directories if they are missing.
- **SQLite Pragmas (Foreign Keys)**: By default, SQLite does not enforce foreign key constraints. To ensure database integrity, we listen to connection events in `database.py` and execute the pragma command:
  ```python
  @event.listens_for(engine, "connect")
  def set_sqlite_pragma(dbapi_connection, connection_record):
      cursor = dbapi_connection.cursor()
      cursor.execute("PRAGMA foreign_keys=ON")
      cursor.close()
  ```

---

## 2. Table Creation

On startup, `Base.metadata.create_all(engine)` is run inside `initialize_database()`.
This reads the declarative schema in `models.py` and generates tables for:
- `departments`
- `courses`
- `students`
- `face_embeddings`
- `attendance`
- `attendance_logs`

---

## 3. Startup Seeding Mechanism

To ensure the application is immediately usable, the system automatically checks and seeds default records:

1. **Departments Seeding**:
   Checks if the `departments` table is empty. If it is, the system inserts:
   - **Computer Science & Engineering** (Code: `CSE`)
   - **Electronics & Communication Engineering** (Code: `ECE`)
   - **Mechanical Engineering** (Code: `ME`)

2. **Courses Seeding**:
   Checks if the `courses` table is empty. If it is, the system inserts:
   - **Bachelor of Technology in CSE** (Code: `BTECH-CSE`, linked to `CSE`)
   - **Master of Technology in CSE** (Code: `MTECH-CSE`, linked to `CSE`)
   - **Bachelor of Technology in ECE** (Code: `BTECH-ECE`, linked to `ECE`)
   - **Bachelor of Technology in ME** (Code: `BTECH-ME`, linked to `ME`)
