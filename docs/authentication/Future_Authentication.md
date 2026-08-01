# Future Authentication & Scale Specification

This document details the scalability strategies and technical foundations embedded in the current design to support transition from local desktop authentication to cloud-scale, federated Identity & Access Management (IAM) systems.

---

## 1. Cloud & API Transition Blueprint

The local architecture isolates user authentication checks within a service wrapper. This design enables a smooth transition to client-server API models:

```mermaid
flowchart TD
    subgraph Local_Desktop_Client [Current Local Context]
        UI[CustomTkinter App] -->|Direct call| LocalAuth[Local AuthService]
        LocalAuth -->|SQLite Query| SQLite[(Local SQLite)]
     color end
    
    subgraph Future_Enterprise_Scale [SaaS Target Context]
        UI_Scale[CustomTkinter App] -->|HTTPS Call| API_GW[FastAPI Gateway]
        API_GW -->|Token Validate| JWT[JWT Validator]
        JWT -->|Scopes Query| LDAP[(Active Directory / LDAP)]
    end
```

---

## 2. Advanced Security Features Roadmap

### 2.1 JWT (JSON Web Tokens) & Stateless Sessions
*   **Design Fit**: When transitioning to a REST API, the desktop client will substitute the local RAM session manager with an HTTP request interceptor. 
*   **Mechanic**: On successful credentials post to `/api/v1/auth/token`, the server issues a signed RS256 token. The client app stores the token in memory and appends it as a header (`Authorization: Bearer <token>`) in subsequent request packages.

### 2.2 Enterprise LDAP & Active Directory Integration
*   **Design Fit**: Large universities and enterprises require unified sign-on.
*   **Integration**: The service layer's `authenticate_user()` routine can be extended to bind against LDAP servers:
    ```python
    # Future target integration logic
    # import ldap
    # conn = ldap.initialize("ldap://corp-domain.edu")
    # conn.simple_bind_s(dn, password)
    ```
    If bind succeeds, the system maps the AD group variables directly to roles.

### 2.3 Federated Sign-In (OAuth2 / OpenID Connect)
*   **Design Fit**: Allows administrators and faculty to log in using Google Workspace or Microsoft Azure AD credentials.
*   **Workflow**:
    1.  The desktop app launches a secure native browser view or redirect loop.
    2.  The user signs in on the Google/Microsoft portal.
    3.  Google/Microsoft returns an authentication callback with an authorization code.
    4.  The application exchanges the code for tokens, mappings matching email addresses to profiles.

### 2.4 Multi-Factor Authentication (MFA)
*   **Mechanic**: Enforce Time-Based One-Time Passwords (TOTP) using standard apps (e.g. Google Authenticator).
*   **Integration**:
    *   During setup, the system generates a QR code representing a cryptographically secure random base32 seed.
    *   During login, a secondary entry panel is displayed requesting the active 6-digit verification code before creating the session.

### 2.5 Biometric Recognition Sign-In
*   **Mechanic**: Leverage the face recognition engine as an authentication factor for faculty.
*   **Workflow**: Instead of a password, the camera captures a live frame of the administrator, extracts the embedding, and compares it with their registered record to authorize dashboard entry (typically coupled with a PIN to prevent static photo spoofing).
