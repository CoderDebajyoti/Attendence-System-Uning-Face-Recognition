# Workflow Diagrams

## 1. Purpose
The **Workflow Diagrams** document visualizes administrative and operational workflows in the Face Recognition Attendance System. These diagrams model user actions, service layers, and database transactions to guide development.

---

## 2. Overview
The system coordinates interactions between administrators, faculty, databases, and biometric camera models. This document details these interactions for eight core administrative workflows.

---

## 3. Core Workflows (Mermaid Visualizations)

### 3.1 Student Registration Workflow
This workflow traces a student from initial data entry through profile creation, validation, and database storage.

```mermaid
sequenceDiagram
    autonumber
    actor Admin
    participant App as GUI Form
    participant SS as StudentService
    participant VS as ValidationService
    participant DB as Database
    
    Admin->>App: Input registration fields (Name, DOB, Code, etc.)
    App->>VS: Validate input formatting & constraints
    VS-->>App: Input formatting is valid
    App->>SS: register_student(profile_data)
    SS->>VS: Check if student_code/email already exists
    VS-->>SS: Identifiers are unique
    SS->>DB: INSERT into students & student_profiles
    DB-->>SS: Student record created successfully
    SS-->>App: Registration successful
    App-->>Admin: Show confirmation message
```

---

### 3.2 Faculty Registration Workflow
This workflow shows the steps for onboarding a new faculty member and creating their system credentials.

```mermaid
sequenceDiagram
    autonumber
    actor Admin
    participant App as GUI Form
    participant FS as FacultyService
    participant US as UserService
    participant DB as Database
    
    Admin->>App: Input faculty fields (Employee Code, Name, Role, etc.)
    App->>FS: register_faculty(faculty_data)
    FS->>US: create_system_user(username, email, default_role='Faculty')
    US->>DB: INSERT into users (credentials & password hash)
    DB-->>US: User ID returned
    US-->>FS: User ID linked
    FS->>DB: INSERT into faculty (employee_code, user_id, department_id)
    DB-->>FS: Faculty record created successfully
    FS-->>App: Registration complete
    App-->>Admin: Show success dialog with login details
```

---

### 3.3 Enrollment Workflow
Details how students are assigned to courses, semesters, and sections.

```mermaid
flowchart TD
    Start[Request Enrollment] --> ActiveCheck{Is Student Profile Active?}
    ActiveCheck -->|No| Reject[Reject: Student profile is inactive]
    ActiveCheck -->|Yes| CourseAlign{Does Course match Department?}
    CourseAlign -->|No| Reject
    CourseAlign -->|Yes| CapacityCheck{Is Section Capacity < Limit?}
    CapacityCheck -->|No| Reject
    CapacityCheck -->|Yes| WriteDB[Save Course, Semester, & Section mappings]
    WriteDB --> FaceCheck{Are biometric face embeds registered?}
    FaceCheck -->|No| SetPending[Set status = 'Pending_Biometrics']
    FaceCheck -->|Yes| SetActive[Set status = 'Active' & Grant attendance eligibility]
```

---

### 3.4 Student Transfer Workflow
Visualizes the process for transferring a student between courses or departments.

```mermaid
sequenceDiagram
    autonumber
    actor Admin
    participant ES as EnrollmentService
    participant VS as ValidationService
    participant DB as Database
    
    Admin->>ES: Request transfer (Student ID, New Course ID, New Section ID)
    ES->>VS: Validate new Course exists & Section has capacity
    VS-->>ES: Validated
    ES->>DB: Update student's course_id & section_id
    ES->>DB: Create student transfer history log
    DB-->>ES: Records updated
    ES-->>Admin: Show transfer confirmation
```

---

### 3.5 Faculty Assignment Workflow
Shows how faculty members are assigned to teach specific subjects.

```mermaid
sequenceDiagram
    autonumber
    actor Admin
    participant FS as FacultyService
    participant DB as Database
    
    Admin->>FS: Assign subject to instructor (Faculty ID, Subject ID)
    FS->>DB: Query subject department & faculty department
    DB-->>FS: Return department details
    alt Departments match
        FS->>DB: Update subject's faculty_id to Faculty ID
        DB-->>FS: Saved
        FS-->>Admin: Assignment complete
    else Departments do not match (Cross-assignment)
        FS->>FS: Check HOD administrative override permissions
        alt Override approved
            FS->>DB: Update subject's faculty_id to Faculty ID
            DB-->>FS: Saved
            FS-->>Admin: Cross-assignment complete
        else Override rejected
            FS-->>Admin: Reject: Department mismatch
        end
    end
```

---

### 3.6 Class Creation Workflow
Timetable scheduling. Map subjects, sections, classrooms, and instructors to time slots.

```mermaid
flowchart TD
    Start[Create Schedule Slot] --> CheckFac{Is faculty available at this time?}
    CheckFac -->|No| Reject[Reject: Schedule overlap for faculty]
    CheckFac -->|Yes| CheckRoom{Is classroom open at this time?}
    CheckRoom -->|No| Reject
    CheckRoom -->|Yes| SaveSchedule[Save timetable record to class_schedules]
```

---

### 3.7 Bulk Import Workflow
Bulk file imports and transactional rollback safety logic.

```mermaid
flowchart TD
    File[CSV File Selected] --> ValidateHeaders{Do headers match template?}
    ValidateHeaders -->|No| RejectAll[Reject file: Header format invalid]
    ValidateHeaders -->|Yes| StartTransaction[Start database transaction]
    StartTransaction --> Loop[Loop: Process rows]
    Loop --> ValidateRow{Is row data valid?}
    ValidateRow -->|No| CollectError[Add validation error to log]
    ValidateRow -->|Yes| QueueRow[Queue INSERT statement]
    QueueRow --> Next{More rows?}
    CollectError --> Next
    Next -->|Yes| Loop
    Next -->|No| CheckErrors{Any validation errors?}
    CheckErrors -->|Yes| Rollback[Rollback transaction & show error list]
    CheckErrors -->|No| Commit[Commit transaction & show success confirmation]
```

---

### 3.8 Profile Update Workflow
Details how users update their profile details.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant App as Profile Edit GUI
    participant VS as ValidationService
    participant DB as Database
    
    User->>App: Edit email or phone field, select photo
    App->>VS: Validate email formatting & phone number format
    VS-->>App: Formatting is valid
    App->>DB: Update email & phone fields
    alt Photo selected
        App->>App: Copy photo to local directory
        App->>DB: Update profile photo file path
    end
    DB-->>App: Profiles updated successfully
    App-->>User: Show success message
```

---

## 4. Business Rules
- **Rollback Consistency**: Bulk imports must use database transactions to prevent partial datasets from being saved if an error occurs.
- **Schedule Overlaps**: Schedule check validations must run immediately during input changes to prevent scheduling conflicts before submitting forms.

---

## 5. Design Decisions
- **Transaction Boundaries**: Grouping bulk import validations inside a single database transaction allows the system to roll back updates if database conflicts occur, keeping the database consistent.
- **Granular Validations**: Running validation checks at the application/service layer before database write calls provides user-friendly error messages instead of raw database constraint error codes.

---

## 6. Future Improvements
- **Live Sync Updates**: Build WebSocket integrations to push real-time updates to UI grids when background sync tasks complete.
- **Conflict Visualizer**: Add a visual conflict dashboard that displays timetable scheduling conflicts (e.g., overlapping classrooms or double-booked faculty) during timetable creation.

---

## 7. References to Related Modules
- [Management Overview](file:///c:/GitHub/Attendence-System-Uning-Face-Recognition/docs/management/Management_Overview.md)
- [Class Module](file:///c:/GitHub/Attendence-System-Uning-Face-Recognition/docs/management/Class_Module.md)
- [Import & Export](file:///c:/GitHub/Attendence-System-Uning-Face-Recognition/docs/management/Import_Export.md)
