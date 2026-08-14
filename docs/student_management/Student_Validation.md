# Student Profile Input Validation Specifications

This document defines the validation rules, data constraints, format checks, and error feedback logic enforced inside the `StudentService`.

---

## 1. Input Field Constraints

All inputs submitted through the `StudentFormDialog` are processed and validated prior to database insertion. The table below lists the validation rules:

| Field Name | DB Column | Required | Validation Rule |
| :--- | :--- | :--- | :--- |
| **Student ID** | `student_code` | Yes | Unique string (alphanumeric, e.g., STD202601). Enforced globally. |
| **Roll Number** | `roll_number` | No | Unique string if provided. Nullable. |
| **First Name** | `first_name` | Yes | Non-empty string. |
| **Last Name** | `last_name` | Yes | Non-empty string. |
| **Email** | `email` | Yes | Must match format: `name@domain.ext` |
| **Phone** | `phone` | Yes | Must match format: `+?[\d\s-]{7,20}` |
| **Date of Birth**| `date_of_birth`| Yes | Format: `YYYY-MM-DD`. Must represent a past date. |
| **Enrollment Date**| `enrollment_date`| Yes | Format: `YYYY-MM-DD`. Valid calendar date. |
| **Year** | `year` | Yes | Integer boundary: `1 <= Year <= 4` |
| **Semester** | `semester` | Yes | Integer boundary: `1 <= Semester <= 8` |
| **Status** | `status` | Yes | Must be: `Active`, `Inactive`, `Graduated`, `Suspended` |

---

## 2. Validation Flow Sequence

The service processes validations in a specific order:

1. **Empty Fields Check**: Scans all fields marked as required. Blocks if any are empty or whitespace.
2. **Format Parsers**: Runs regular expressions on **Email** and **Phone** columns. Runs `datetime.strptime` on **Date of Birth** and **Enrollment Date** keys.
3. **Domain Boundary Check**: Confirms **Year** and **Semester** numbers fall within academic boundaries (e.g. Year 4, Semester 8 max).
4. **Collision Checks (Database Queries)**:
   - Queries `StudentRepository.get_by_code(code)`. Collision fails if found (except when editing the same record).
   - Queries `StudentRepository.get_by_roll_number(roll)`. Collision fails if found.
5. **Database Save Commit**: Proceeds to commit transaction. Any exception triggers a rollback and returns failure.

---

## 3. UI Error Dialog Boxes

When a validation constraint is breached:
- The service returns `(False, error_message)`.
- The controller coordinates this feedback to the form dialog.
- The dialog spawns a blocking `MessageBox` with `icon_type="error"` displaying the specific validation failure message.
- The form inputs are left intact, allowing the user to correct the error and try again.
