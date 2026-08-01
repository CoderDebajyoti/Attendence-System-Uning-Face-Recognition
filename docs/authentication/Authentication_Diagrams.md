# Authentication & Authorization Architecture Diagrams

This document consolidates all architectural, sequencing, and state transitions diagrams for the **Face Recognition Attendance System** authentication design.

---

## 1. Authentication Flow (Sequencing)

Details the request flow from login view submission to credential hashing and dashboard dispatch.

```mermaid
sequenceDiagram
    autonumber
    actor User as Admin/Faculty
    participant UI as CustomTkinter GUI
    participant AuthCtrl as AuthController
    participant AuthService as AuthService
    participant HashEngine as Hashing Engine
    participant DB as Database
    
    User->>UI: Enter Username & Password + Click "Login"
    UI->>AuthCtrl: Submit login credentials
    AuthCtrl->>AuthCtrl: Client-side input validation checks
    alt Validation fails
        AuthCtrl-->>UI: Display generic validation error
    else Validation passes
        AuthCtrl->>AuthService: authenticate_user(username, password)
        AuthService->>DB: Query User record by username
        alt User not found
            AuthService->>HashEngine: Run dummy verify to match timing latency
            AuthService-->>AuthCtrl: Raise AuthenticationError (Generic message)
        else User found
            DB-->>AuthService: Return password hash & is_active status
            AuthService->>HashEngine: verify_password(password, stored_hash)
            HashEngine-->>AuthService: Return match boolean
            alt Hash does not match
                AuthService-->>AuthCtrl: Raise AuthenticationError (Generic message)
            else Hash matches
                AuthService->>AuthService: Create RAM Session mapping
                AuthService-->>AuthCtrl: Return Session Context
                AuthCtrl->>UI: Route to Dashboard (Unmount Login view)
                UI-->>User: Render Dashboard
            end
        end
    end
```

---

## 2. RBAC Structure (Inheritance Diagram)

Visualizes how permissions inherit from lower roles to higher administration tiers.

```mermaid
graph TD
    SuperAdmin[Super Admin] -->|Inherits all permissions| Admin[Administrator]
    Admin -->|Inherits permissions| Faculty[Faculty]
    Faculty -->|Inherits permissions| LabAssistant[Lab Assistant]
    
    subgraph Future_SaaS [Future Extensions]
        Student[Student]
        Viewer[Viewer]
    end
```

---

## 3. Permission Verification Flow

Shows how security intercepts are processed at the boundary of service executions.

```mermaid
flowchart TD
    Request[Invoke Service Method e.g., create_user] --> Intercept{requires_permission Decorator}
    Intercept -->|Check session permissions| Valid{Permission Mapped?}
    Valid -- Yes --> Exec[Execute Repository Database Call]
    Valid -- No --> Raise[Raise PermissionDeniedException]
    
    Exec --> Return[Return Data to Controller]
    Raise --> UI[Render Warning Panel in GUI]
```

---

## 4. Session Lifecycle State Diagram

Tracks session state transitions from initial startup validation to timeouts and explicit logouts.

```mermaid
stateDiagram-v2
    [*] --> Disconnected
    Disconnected --> Active : Login Validated (Generate RAM Token)
    Active --> Active : Heartbeat Reset (Mouse/Key Event)
    Active --> IdleTimeout : Inactivity exceeds limit (e.g., 15 mins)
    Active --> Terminated : Explicit click Logout / Close App
    Active --> AbsoluteTimeout : Lifetime limit reached (12 hours)
    
    IdleTimeout --> Disconnected : Purge Memory & Show Login View
    AbsoluteTimeout --> Disconnected : Purge Memory & Show Login View
    Terminated --> Disconnected : Purge Memory & Show Login View
```

---

## 5. Account Recovery State Diagram

Maps account states from creation (temporary password force change) to lockout and deactivation overrides.

```mermaid
stateDiagram-v2
    [*] --> ActiveAccount
    ActiveAccount --> LockedOut : 5 Failed Attempts
    ActiveAccount --> Disabled : Admin Set is_active = False
    
    LockedOut --> ActiveAccount : Lockout Timer Expires (15 mins)
    LockedOut --> PasswordResetState : Admin Manual Override Reset
    
    Disabled --> ActiveAccount : Admin Manual Enable
    
    ActiveAccount --> PasswordResetState : Reset request submitted
    PasswordResetState --> ForcePasswordChange : Login with Temp Password
    ForcePasswordChange --> ActiveAccount : User saves new password hash
```

---

## 6. Dashboard Navigation by Role

Illustrates the navigation views rendered in the CustomTkinter sidebar according to the authenticated user's role:

```mermaid
graph TD
    UserSession[Active User Session] --> RoleSwitch{Evaluate Role ID}
    
    RoleSwitch -->|Super Admin| SAD[Super Admin Dashboard]
    RoleSwitch -->|Administrator| AD[Admin Dashboard]
    RoleSwitch -->|Faculty| FD[Faculty Dashboard]
    RoleSwitch -->|Lab Assistant| LAD[Lab Assistant View]
    
    subgraph SAD_Menus [Super Admin Panels]
        SAD --> SA1[Global Configuration]
        SAD --> SA2[Log Diagnostics Terminal]
        SAD --> SA3[Database Backups & Restore]
        SAD --> SA4[User Provisioning Controls]
    end
    
    subgraph AD_Menus [Admin Panels]
        AD --> AD1[User Profiles Registry]
        AD --> AD2[Departments & Courses Setup]
        AD --> AD3[Faculty Mappings]
    end
    
    subgraph FD_Menus [Faculty Panels]
        FD --> FD1[Student Profiles Management]
        FD --> FD2[Face Dataset Capture Wizard]
        FD --> FD3[Attendance Review & Tracking]
        FD --> FD4[Metrics Reports Exporter]
    end
    
    subgraph LAD_Menus [Assistant Panels]
        LAD --> LA1[Live Verification Camera Loop]
        LAD --> LA2[Daily Attendance Review]
    end
```

---

## 7. Audit Logging Process Flow

Traces how security logs are generated, sanitized of passwords/hashes, and saved.

```mermaid
flowchart LR
    Trigger[Security Event: e.g., Login Success] --> Service[Audit Log Service]
    Service --> Strip[Sanitize: Strip sensitive credentials inputs]
    Strip --> WriteDB[Write log row to SQL database table]
    Strip --> WriteFile[Append formatted line to rolling system.log]
```
