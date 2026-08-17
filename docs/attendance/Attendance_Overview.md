# Attendance Management Overview

This module governs the process of validating biometric classification matches from the Face Recognition Engine and writing transaction-safe attendance records to the database.

## System Workflow

```mermaid
graph TD
    A[Camera Capture Frame] --> B[Face Detector Service]
    B --> C[Face Recognition Service]
    C --> D{Is Student Recognized?}
    D -- No --> E[Display Unknown Face]
    D -- Yes --> F[Attendance Service]
    F --> G{Check Cooldown Cache}
    G -- Active --> H[Display Already Marked]
    G -- Expired --> I{Auto Mode Configuration}
    I -- Yes --> J[Mark Attendance in DB]
    I -- No --> K[Pending Confirmation Dialog]
    K -- Confirm --> J
    K -- Cancel --> L[Reset view state]
    J --> M[Update Cooldown Cache]
```

## Features Complete

1. **Biometric Integration**: Seamlessly maps LBPH recognition distance matches to checked identities.
2. **Duplicate Prevention**: Dual-layer protection using in-memory cooldown cache and SQLite database unique constraints.
3. **Session Windows**: Group logs under active course/class date intervals.
4. **Manual Override**: Supports supervised check-in records logging source = MANUAL.
5. **Interactive UI**: Real-time feedback badges (✓ Recorded, ℹ Already Marked, ⚠ Error).
