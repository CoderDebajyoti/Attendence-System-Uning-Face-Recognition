# Timezone Strategy & Time Handling

To maintain data audit integrity across environments:

## UTC Timestamping
* Database audit timestamps (`created_at`, `updated_at`, `timestamp` logs) are captured and saved in UTC timezone format.
* To prevent warnings in Python 3.12+, timezone-aware UTC datetime instances are generated using `datetime.now(timezone.utc)` rather than deprecated `utcnow()`.

## Local Check-In Times
* Daily check-in dates (`date` column, e.g. `2026-08-16`) and check-in times (`time_in` column, e.g. `09:12:31`) are logged using the local system time of the application server.
* Displays on the frontend format raw `HH:MM:SS` strings into local 12-hour values with AM/PM indicators (e.g. `09:12 AM`).
