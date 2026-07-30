# Face Recognition Attendance System - User Flows

This document details the distinct workflows and interactions for each user role: **Administrator**, **Faculty Member**, and **Student**. These flows map the visual transitions and functional steps of the application's graphical interface.

---

## 1. System Administrator Flow

The System Administrator handles configuration, directory updates, user role assignments, and system-wide audit tracking.

```mermaid
flowchart TD
    AdminStart([Admin Log In]) --> AdminDashboard[Load Admin Dashboard]
    
    AdminDashboard --> SelectAdminAction{Select Action}
    
    %% Option 1: Manage Faculty accounts
    SelectAdminAction -->|Manage Accounts| UserAccounts[View Registered Faculty/User list]
    UserAccounts --> CreateUser[Create User Profile & Set Password]
    CreateUser --> AssignRole[Assign Role: Admin vs Faculty]
    AssignRole --> SaveAccount[Write to Database]
    SaveAccount --> UserAccounts
    
    %% Option 2: Config Settings
    SelectAdminAction -->|Global Settings| ConfigSettings[Configure Camera Sources / RTSP Links]
    ConfigSettings --> EmbedSettings[Adjust Recognition Thresholds & Cooldowns]
    EmbedSettings --> ConnSettings[Configure DB Connections: SQLite vs PostgreSQL]
    ConnSettings --> SaveSettings[Save config.json]
    SaveSettings --> AdminDashboard
    
    %% Option 3: Logs & Backups
    SelectAdminAction -->|System Audit| ViewLogs[View Logging Panel]
    ViewLogs --> ExportAuditLogs[Export audit_trail.log]
    ViewLogs --> DBBackup[Trigger Database Backup]
    DBBackup --> BackupDone[Create app_database_backup.db]
    BackupDone --> AdminDashboard
```

---

## 2. Faculty User Flow

Faculty members manage courses, subjects, student registrations, run daily camera tracking panels, and download reports.

```mermaid
flowchart TD
    FacultyStart([Faculty Log In]) --> FacultyDashboard[Load Faculty Dashboard]
    
    FacultyDashboard --> SelectFacultyAction{Select Action}
    
    %% Option 1: Student Enrollment
    SelectFacultyAction -->|Student Enroller| StudentGrid[Search/Filter Students]
    StudentGrid --> EnrollNew[Add New Student Profile]
    EnrollNew --> StartCapture[Initiate Camera Enrollment Wizard]
    StartCapture --> GenerateBiometrics[Save Face Embeddings]
    GenerateBiometrics --> StudentGrid
    
    %% Option 2: Class Session Attendance
    SelectFacultyAction -->|Scan Attendance| SelectClass[Select Course & Subject]
    SelectClass --> LaunchScanner[Open Scanning Monitor]
    LaunchScanner --> StartCam[Start Real-Time Process Loop]
    StartCam --> MarkPresent[Display Success Overlay on Canvas]
    MarkPresent --> EndSession[Close Camera Scanner]
    EndSession --> EditLogs{Manual Adjustments Needed?}
    EditLogs -- Yes --> ModifyRecord[Faculty Modifies Attendance Status manually]
    ModifyRecord --> UpdateDb[Save modifications & Log Audit Trail]
    ModifyRecord --> ViewSessionSummary[View Current Session Summary]
    EditLogs -- No --> ViewSessionSummary
    ViewSessionSummary --> FacultyDashboard
    
    %% Option 3: Reports
    SelectFacultyAction -->|Analytics Panel| ReportFilter[Select Date Range, Course, Student ID]
    ReportFilter --> PlotCharts[View Interactive Attendance Graphs]
    PlotCharts --> SaveReport[Export Report: CSV / Excel / PDF]
    SaveReport --> FacultyDashboard
```

---

## 3. Student Interaction Flow

Students are the subjects of verification. They do not log into the application; instead, their interaction is contactless via the face recognition terminal.

```mermaid
flowchart TD
    StudentStart([Student Approaches Attendance Camera]) --> StandInFrame[Stand within camera capture frame]
    StandInFrame --> RecognitionLoop[System processes frames in background thread]
    
    RecognitionLoop --> MatchCheck{Face Identified & Similarity >= Threshold?}
    
    %% Path A: Match Found
    MatchCheck -- Yes --> CooldownCheck{Already marked for this session?}
    CooldownCheck -- No --> RegisterMatch[System logs Attendance & Play Success Alert]
    RegisterMatch --> OverlaySuccess[Canvas displays: 'Green Box' + Name + ID]
    OverlaySuccess --> Complete([Walk away: Attendance Logged])
    
    CooldownCheck -- Yes --> OverlayAlready[Canvas displays: 'Yellow Box' + 'Already Marked']
    OverlayAlready --> Complete
    
    %% Path B: Match Failed
    MatchCheck -- No --> OverlayUnknown[Canvas displays: 'Red Box' + 'Unknown Face']
    OverlayUnknown --> RequestManual{Retry or Manual Register?}
    RequestManual -->|Retry| StandInFrame
    RequestManual -->|Seek Instructor| ReportToFaculty[Provide Student ID to Faculty for Manual entry]
    ReportToFaculty --> Complete
```
