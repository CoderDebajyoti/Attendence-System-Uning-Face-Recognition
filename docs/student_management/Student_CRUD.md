# Student Database CRUD Operation Details

This document explains the CRUD (Create, Read, Update, Delete) database transactions and SQL statements executed by the `StudentRepository`.

---

## 1. Create Operation (Insert)

When registering a student profile, the repository maps a dictionary into the `Student` SQLAlchemy model and commits it:

- **ORM Call**: `session.add(student)`
- **SQL Execution**:
  ```sql
  INSERT INTO students (
      student_code, roll_number, first_name, last_name, email, phone, 
      date_of_birth, gender, address, department_id, course_id, 
      year, semester, enrollment_date, status, face_dataset_status, is_active
  ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
  ```

---

## 2. Read Operation (Select & Filter)

To query students, we join relations using SQLAlchemy's `joinedload` to prevent lazy loading errors after session closure:

- **ORM Call**:
  ```python
  session.query(Student).options(
      joinedload(Student.department),
      joinedload(Student.course)
  ).filter(Student.is_active == True)
  ```
- **SQL Execution**:
  ```sql
  SELECT students.*, departments.*, courses.*
  FROM students
  LEFT OUTER JOIN departments ON departments.id = students.department_id
  LEFT OUTER JOIN courses ON courses.id = students.course_id
  WHERE students.is_active = 1;
  ```

---

## 3. Update Operation (Update)

To update attributes, we retrieve the record, modify field values, and commit the transaction:

- **ORM Call**: `session.commit()`
- **SQL Execution**:
  ```sql
  UPDATE students 
  SET first_name = ?, last_name = ?, email = ?, phone = ?, status = ?, year = ?, semester = ?
  WHERE id = ?;
  ```

---

## 4. Delete Operation (Delete)

Deleting a student record executes a cascade delete, which removes all records in dependent tables:

- **ORM Call**: `session.delete(student)`
- **SQL Execution**:
  ```sql
  DELETE FROM students WHERE id = ?;
  ```
- **Cascading Constraints**:
  In `models.py`, cascading rules are set up:
  - `face_embeddings` table records are deleted via `ondelete="CASCADE"`.
  - `attendance` table records are deleted via `ondelete="CASCADE"`.
  - `attendance_logs` table records are deleted via `ondelete="CASCADE"`.
