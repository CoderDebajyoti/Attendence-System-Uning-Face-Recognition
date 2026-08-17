# Attendance Duplicate Prevention

This document details how the Face Recognition Attendance System prevents duplicate attendance records.

## Problem Description
During live face tracking, the webcam processor captures multiple frames per second. A student sitting in front of the camera would trigger dozens of successful face recognition matches consecutively. If unchecked, this would result in thousands of database entries for a single class check-in.

## Prevention Policies
To combat this, the system enforces two distinct layers of duplicate prevention:

### 1. In-Memory Cooldown Cache
The `AttendanceService` maintains an in-memory dictionary cache tracking recent successful check-ins:
`self.cooldown_cache = {student_id: datetime_object_local}`

- **Check-in Request**: When a face is recognized, the service checks `is_in_cooldown(student_id)`.
- **Validation**: If `current_time - last_check_in_time` is less than `cooldown_minutes` (default 30), the check-in is immediately skipped.
- **Benefits**: Bypasses heavy database queries on consecutive camera frames, ensuring the GUI thread remains responsive.

### 2. Database Unique Constraints
If the memory cache is cleared or a student checks in after the cooldown period but on the same date/session:
- The `attendance` table enforces a database-level `UniqueConstraint`:
  `UniqueConstraint('student_id', 'date', 'session_id', name='uq_student_date_session')`
- **Graceful Handling**: `AttendanceRepository.find_record` checks for an existing row prior to insertion. If a database collision occurs, the transaction is safely rolled back, and the service returns a structured `already_marked=True` response instead of crashing.
