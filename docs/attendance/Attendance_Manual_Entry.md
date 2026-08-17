# Manual Attendance Entries

This document details administrative manual overrides for recording and correcting attendance.

## Objective
If a student forgets their ID card, the camera lens is blocked, or biometrics fail under bad lighting, administrators must be able to log attendance manually.

## Core Rules
1. **Source Labeling**: All manual entries must save `source = "MANUAL"` in the database. Under no circumstances should manual edits masquerade as face recognition events.
2. **Note/Reason Obligation**: Manual overrides require entering a brief justification note (e.g. `"Biometric bypass"`, `"Approved late entry"`) to maintain audit integrity.
3. **Transaction Safety**: Manual entries are validated against standard database unique constraints to prevent double-logging for a single session.

## UI Forms
- **Mark Attendance Manually Dialog**: Displays a student selection dropdown, date input field, status selector (PRESENT, LATE, ABSENT, EXCUSED), and note field.
- **Correction Dialog**: Allows correcting an existing status (e.g. converting `LATE` to `PRESENT` due to a verified transit delay).
