# Security & Audit Guidelines

## Biometric Data Separation
* Attendance logs never contain face embeddings, feature templates, or raw bounding box crops.
* Logs are linked using stable foreign key constraints pointing to the standard Student database entity ID.

## Privacy Logging Safeguards
* Logger logs never dump biometric vectors, numpy array representations, or personal images.
* Match diagnostics only log anonymized database student codes, confidence distance metrics, and timestamp counts.

## System Audits
* Every manual override check-in logs:
  * The identity of the operator initiating the correction (`updated_by` / `marked_by`).
  * The modified status flag.
  * The updated UTC timestamp.
* Silent deletes are prohibited; all deletions require confirmation.
