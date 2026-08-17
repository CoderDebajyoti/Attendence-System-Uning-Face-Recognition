# Attendance Testing Suite

Unit test coverages are located at [test_attendance_service.py](file:///c:/GitHub/Attendence-System-Uning-Face-Recognition/tests/unit/test_attendance_service.py):

## Test Scenarios

1. **Successful biometric check-in**: Confirms valid matches record PRESENT/LATE in database.
2. **Duplicate check-in prevention**: Verifies second matches within the same day return cached or DB records without duplicate writes.
3. **Recognition cooldown window**: Simulates cooldown timer expiry and cache eviction.
4. **Manual override logging**: Tests writing manual logs containing source = MANUAL.
5. **Attendance correction updates**: Confirms status updates log operator audit details.
6. **Statistics calculations**: Verifies department/course filters and rate aggregation metrics.

## Running Tests

Execute from the repository root:
```powershell
.venv\Scripts\pytest
```
