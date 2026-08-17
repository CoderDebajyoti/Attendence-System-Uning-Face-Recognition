# Attendance Workflows

## Biometric Match Workflow

1. A face match registers with a score above the threshold.
2. The page checks if the `student_id` is in the `AttendanceService` cooldown cache.
3. If not in cooldown, depending on settings:
   * **Auto Mode**: The check-in is logged automatically.
   * **Confirmation Mode**: Prompt appears on the left panel. User must click "Confirm Present" to write to DB.
4. Cooldown cache updates on success.

## Manual Override Workflow

1. Registrar navigates to the **Attendance** tracking panel.
2. Clicks the "Mark Attendance Manually" action.
3. Selects student profile, logs correct date, chooses status (PRESENT, LATE, ABSENT, EXCUSED), and records override reasons.
4. Saving commits a transaction-safe insert with source = MANUAL.
