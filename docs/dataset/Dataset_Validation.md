# Dataset Validation Checklist

This document details the checklist audits conducted by the `DatasetValidationService` before marking a dataset status as `READY`.

---

## Validation Checklist Audits

A face dataset must satisfy the following checklist constraints:

| Check | Constraint | Trigger Condition / Rejection Reason |
| :--- | :--- | :--- |
| **Directory Check** | Path exists. | Rejects if the student's crop directory is missing on disk. |
| **Image Count** | Count $\ge$ target count. | Rejects if the total count is less than the target count (default 25). |
| **Readability** | Files can be read by `cv2.imread`. | Rejects if any files are missing, corrupted, or unreadable. |
| **Dimensions** | $112 \times 112$ pixels. | Rejects if any image width/height differs from the target alignment size. |
| **Face Check** | Exactly 1 face per image. | Rejects if any saved crop contains zero or multiple faces when evaluated. |

---

## Audit Output Structure

The service returns a structured dictionary:
*   `success` (bool): `True` if all validation checks pass.
*   `status` (str): `READY` if successful, otherwise `NEEDS_UPDATE` or `INVALID`.
*   `errors` (list): Detailed list of failure reasons.
*   `successes` (list): Detailed list of passed checks.
*   `validation_result` (str): Semicolon-separated string summary.
*   `last_validation` (str): Timestamp of the audit.
