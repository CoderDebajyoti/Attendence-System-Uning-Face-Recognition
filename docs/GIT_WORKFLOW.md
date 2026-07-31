# Face Recognition Attendance System - Git Workflow Guide

This document establishes the version control guidelines, branching strategies, and commit rules to keep the repository history clean, semantic, and auditable.

---

## 1. Branching Strategy

The repository follows a **Trunk-Based Development** model with short-lived topic/feature branches. This layout reduces merge conflicts and keeps the project ready for CI integration.

- **Main Branch (`main`)**: Protected. Contains stable, build-passing code. Direct pushes are blocked. Modifications are introduced solely via Pull Requests.
- **Short-Lived Feature Branches (`feat/*`)**: Used for developing new capabilities (e.g., `feat/auth-verification`).
- **Bug Fix Branches (`fix/*`)**: Used for corrective changes (e.g., `fix/camera-feed-dropout`).
- **Refactoring Branches (`refactor/*`)**: Code optimization without logical changes.
- **Documentation Branches (`docs/*`)**: Documentation revisions or additions.

---

## 2. Commit Message Conventions

We adhere to the **Conventional Commits 1.0.0** specification.

### 2.1 Format
```text
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### 2.2 Naming Rules
1. **Type**: Must be one of the following:
   - `feat`: User-facing feature.
   - `fix`: Code correction.
   - `docs`: Document updates.
   - `style`: Formatting change (Black adjustments).
   - `refactor`: Structural rewrite.
   - `test`: Adding/modifying test scripts.
   - `chore`: Modifying build files, configurations, or packages.
2. **Scope**: Context element enclosed in parentheses (e.g., `cv`, `gui`, `db`, `auth`).
3. **Description**: Concise, present-tense sentence structure, starting in lowercase. No period at the end.
4. **Body & Footer**: Detail context and list resolved issues (e.g., `Closes #41`).

---

## 3. Version Tagging & Release Strategy

We follow **Semantic Versioning 2.0.0 (SemVer)**:
- Format: `MAJOR.MINOR.PATCH` (e.g., `1.0.4`)
  - **MAJOR**: Incompatible API or structural changes.
  - **MINOR**: Backward-compatible functionality additions.
  - **PATCH**: Backward-compatible bug fixes.

- **Tagging Command**:
  ```bash
  git tag -a v1.0.0 -m "Release version 1.0.0 stable baseline"
  git push origin v1.0.0
  ```
- **Release Automation**: Pushing a tag starts GitHub actions compiling PyInstaller builds and attaching `.zip` Windows executable distributions to the release draft.

---

## 4. Pull Request Standards & Labels

### 4.1 PR Checklist
- Runs `black --check`, `ruff check`, and `mypy` successfully locally.
- Test suites return 100% success ratings.
- Linked issues are clearly defined in the description footer.
- The description outlines test commands, configurations, and screenshots where applicable.

### 4.2 Standard GitHub Labels
- `bug`: System bugs requiring triage.
- `enhancement`: Feature requests or optimizations.
- `documentation`: Updates to documentation files.
- `triage`: Issues awaiting review.
- `blocking`: High priority tickets preventing progression.
