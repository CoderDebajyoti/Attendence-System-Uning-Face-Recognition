# Student Management UI/UX Specifications

This document outlines the UI designs, layout wireframes, forms grid columns, and dialog box components of the Student Management screen.

---

## 1. Visual Layout Wireframe

The Students page uses a vertical split-pane structure inside the `content_frame`:

```
+--------------------------------------------------------------------------------------+
|                                  Student Management                                  |
+--------------------------------------------------------------------------------------+
| [ Search Input... ] [Search] [All Depts] [All Courses] [All Status] [Reset] [Add St] |
+--------------------------------------------------------------------------------------+
| Student ID   | Name           | Roll No     | Department | Status     | Actions      |
+--------------+----------------+-------------+------------+------------+--------------+
| STD2026001   | Alice Smith    | CSE-26-001  | CSE        | Active     | [👁] [⚙] [🗑]  |
| STD2026002   | Bob Jones      | -           | ECE        | Suspended  | [👁] [⚙] [🗑]  |
+--------------------------------------------------------------------------------------+
| Showing 2 students registered                                                        |
+--------------------------------------------------------------------------------------+
```

---

## 2. Interactive Dialog Designs

### 2.1 Profile Form Dialog (`StudentFormDialog`)
- **Visual Grid Layout**: Split into two vertical columns of input rows.
- **Dynamic Bindings**: Choosing a Department in the left dropdown automatically updates and filters the Course options in the right dropdown.
- **Fields placement**: Required fields are marked with an asterisk (`*`).

### 2.2 Profile Details Modal (`StudentDetailDialog`)
- **Structure**: Uses a scrollable container gridded with Card widgets.
- **Cards list**:
  - **Personal Details**: First Name, Last Name, Gender, Date of Birth.
  - **Contact Information**: Email, Phone, Address.
  - **Academic Allocation**: Department Name, Course Name, Year, Semester.
  - **Enrollment Profile**: Student Code, Roll Number, Enrollment Date, Status.
  - **Biometric Face Dataset**: Dataset Status badge (Ready, Not Registered), Images Count, and a disabled button mapping to the future registration phase.

### 2.3 Delete Confirmation Prompt
- **Trigger**: Clicks trash icon button `[🗑]`.
- **Component**: Spawns warning `MessageBox`.
- **Description**: Highlights that deleting a student profile will cascadingly delete face embeddings and attendance logs. Renders Confirm and Cancel buttons.
