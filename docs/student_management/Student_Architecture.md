# Student Management: Architectural Design

This document details the layered architecture, MVC coordination flow, and decoupled package boundaries of the Student module.

---

## 1. Layered Architecture

The Student module follows Clean Architecture principles by separating UI layout definitions, controller coordination, business logic validations, data access repository queries, and database drivers:

```
[ UI Layer: StudentsPage ] <---> [ Presentation: CTk Dialogs ]
             |
             v
[ Controller: StudentController ]
             |
             v
[ Service: StudentService (Validations & Rules) ]
             |
             v
[ Repository: StudentRepository (SQL Queries) ]
             |
             v
[ Database: SQLite (SQLAlchemy Engines) ]
```

- **GUI (View)**: Renders grids, handles button click event triggers, and positions popup modals. Contains zero SQL statements or transaction commits.
- **Controller**: Directs views requests to domain services. Acts as a thin bridge.
- **Service (Domain)**: Enforces business logic policies. Validates email formats, unique keys, age checks, and formats parameters.
- **Repository (Data Access)**: Executes SQLAlchemy ORM queries, handles eager loading joins, deletes, and calculates count statistics.
- **Database (Core)**: Exposes transactional sessions.

---

## 2. Component Directory Mappings

| Component | Path | Description |
| :--- | :--- | :--- |
| **Model** | `src/core/models.py` | SQLAlchemy Declarative mapping (Student, Course, Department). |
| **DB Core** | `src/core/database.py` | Engine pool setup, sessionmaker, and data seeders. |
| **Repository** | `src/repositories/student_repository.py` | Database operations (list, count, save, update, delete). |
| **Service** | `src/services/student_service.py` | Validations and transaction coordination. |
| **Controller** | `src/controllers/student_controller.py` | Presentation controller. |
| **GUI View** | `src/gui/pages/students.py` | CustomTkinter table grid, forms, and dialog wrappers. |
