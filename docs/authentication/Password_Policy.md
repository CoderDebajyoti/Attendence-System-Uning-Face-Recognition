# Password Security Policy

This document defines the requirements, hashing parameters, and administrative controls governing passwords in the **Face Recognition Attendance System**.

---

## 1. Password Complexity Requirements (NIST 800-63B Guidelines)

In alignment with modern security practices detailed in **NIST SP 800-63B**, complexity rules focus on password length and entropy while avoiding counter-productive rules that lead to predictable pattern alterations:

| Policy Metric | Requirement | Justification |
| :--- | :--- | :--- |
| **Minimum Length** | $12$ characters (recommended $14+$) | Length is the primary defense against offline cracking. |
| **Maximum Length** | $128$ characters | Prevents Denial of Service (DoS) attacks from sending extremely long strings to the CPU hashing engine. |
| **Character Sets** | Unicode allowed (UTF-8) | Supports spaces, emojis, and international characters to encourage natural passphrases (e.g. `correct horse battery staple`). |
| **Breached Verification**| Offline blocklist check | Reject passwords matching the top 10,000 common breached passwords. |

---

## 2. Password Hashing Configurations

Plaintext passwords must never enter storage. Hashing occurs in the service layer using memory-hard functions to resist dictionary/brute-force attacks.

### 2.1 Argon2id (Standard Configuration)
```yaml
Algorithm: Argon2id (RFC 9106)
Memory Cost (m): 65536 KB (64 MB)
Time Cost (t): 3 iterations
Parallelism (p): 4 threads
Salt Size: 16 bytes (cryptographically secure random)
Hash Length: 32 bytes
```

### 2.2 bcrypt (Fallback Configuration)
```yaml
Algorithm: bcrypt (2b variation)
Work Factor (Cost): 12 rounds
Salt Size: 16 bytes
```

---

## 3. Account Lockout Policy (Brute-Force & Credential Stuffing Mitigation)

To prevent online brute-force guessing and automated credential stuffing:

1.  **Threshold**: An account is locked after **$5$ consecutive failed attempts**.
2.  **Duration**: 
    *   Initial lockout lasts for **$15$ minutes**.
    *   Subsequent failed attempts during or immediately after recovery double the lockout window ($30$ mins, $60$ mins, up to a maximum of $24$ hours).
3.  **Persistence**: Lockout counts and timestamps are stored in the database (`failed_login_attempts`, `locked_until`) to prevent attackers from clearing lockouts by restarting the desktop application.
4.  **Logging**: Every lockout event is written to the audit log as a high-severity alert.

---

## 4. Administrative Controls

*   **Temporary Passwords**: Automatically generated when an admin creates a new user. The account is flagged with a database attribute `force_password_change = True`.
*   **Password History**: The system stores the cryptographic hashes of the user's last **$5$ passwords** in a history table (`password_history`). Users cannot change their password to one matching these records.
*   **Forced Expiry (Future)**: Support for configurable expiration ranges (e.g., $90$ days) for high-clearance administrators.
