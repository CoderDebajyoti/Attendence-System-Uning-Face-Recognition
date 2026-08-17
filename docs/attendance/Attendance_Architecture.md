# Attendance Architecture & Separation of Concerns

The module maintains strict boundary separation:

```
[Presentation Layer] (RecognitionPage / AttendancePage)
      │
      ▼
[Controller Layer] (RecognitionController / AttendanceController)
      │
      ▼
[Service Layer] (FaceRecognitionService / AttendanceService)
      │
      ▼
[Repository Layer] (StudentRepository / AttendanceRepository)
      │
      ▼
[Data Model Schema Layer] (Database tables)
```

## Boundaries

1. **Biometric Decoupling**: The `AttendanceService` receives the trusted identity classification but does not handle camera frames, NumPy arrays, or LBPH model prediction calculations.
2. **Transaction Isolation**: Database writes, unique constraints, and rollbacks are isolated within repositories.
3. **Coordinated View Controllers**: GUI widgets do not write directly to DB session connections; they communicate with controller modules.
