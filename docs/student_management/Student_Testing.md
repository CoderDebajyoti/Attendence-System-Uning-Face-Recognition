# Student Management Testing Specifications

This document outlines the testing strategy, unit test suites, and validation coverage checks for the Student module.

---

## 1. Automated Test Suites

Test cases are located under `tests/unit/test_student_service.py` to isolate business validations and database transactions.

Key test areas include:

- **Student Profile Creation**: Verifies that a valid dictionary parses successfully and saves to the database.
- **Student Profile Retrieval**: Confirms eager loading joins fetch department and course descriptions.
- **Student Profile Update**: Checks attributes modifications.
- **Student Profile Deletion**: Verifies cascading delete constraints.
- **Uniqueness Validations**:
  - Confirms registering a duplicate **Student ID** triggers validation failure.
  - Confirms registering a duplicate **Roll Number** triggers validation failure.
- **Input Format Checks**:
  - Invalid email regex inputs fail validation.
  - Invalid phone numbers fail validation.
  - Invalid calendar dates (DOB/Enrollment format violations) fail validation.
  - Out of bounds academic coordinates (e.g. Semester 9, Year 5) fail validation.

---

## 2. Command Line Execution

To run automated test suites in the development environment:

```powershell
.venv\Scripts\pytest tests/
```

This targets unit tests and verifies that database creation scripts, constraints, validations, and statistics logic pass cleanly.
