# Attendance Rules & Duplicate Prevention Policies

## 1. Duplicate Prevention Policy
Students may trigger many face matches within short visual intervals. The system implements a strict policy:
* Only **one** attendance record is saved per student per day per session.
* Submitting a duplicate match returns the existing attendance record and logs an informative feedback payload without writing new table records.

## 2. Recognition Cooldown Mechanism
* To minimize SQLite database queries during a rapid camera loop (30 FPS), successful check-ins are cached in an in-memory dictionary.
* Subsequent matches for that `student_id` are rejected immediately on the client side during the cooldown window.
* Cooldown period is determined by `.env` config variables (e.g. `COOLDOWN_MINUTES=30`).

## 3. Time Classification Rule
* Present vs Late status is determined dynamically.
* If check-in time exceeds the session start time + 15 minutes grace period, the record status is automatically written as `LATE`; otherwise, it is written as `PRESENT`.
