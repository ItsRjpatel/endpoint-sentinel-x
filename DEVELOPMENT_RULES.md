# Development Rules

These core rules govern the architecture, database, API, security, frontend, and agent layers of Endpoint Sentinel X. All developers must adhere to these rules without exception.

---

## General Rules

- **Never bypass repositories**: Always access the database via the Repository layer. Services must not issue raw SQLAlchemy statements.
- **Never access SQLAlchemy sessions directly inside API routes**: Keep routes thin. Route handlers must interact only with Services, which resolve repository layers.
- **Keep business logic inside services**: Repositories must remain purely CRUD-focused. All validation rules and business decisions reside in the Service layer.
- **Keep routes thin**: Presentation layers (endpoints) are only responsible for payload validation, dependency resolution, and response mapping.

---

## Database Rules

- **Every schema change requires an Alembic migration**: No manual database alterations are allowed.
- **Never modify production schema manually**: Always deploy schema updates via Alembic upgrades.
- **UUIDs must remain immutable**: UUID keys represent the external identity token for resources and must never be altered once created.

---

## API Rules

- **Version all endpoints under `/api/v1`**: Avoid breaking client APIs.
- **Use dependency injection**: Inject services and database sessions through FastAPI dependencies (`Depends`).
- **Return consistent response models**: Every endpoint must return a structured response defined by a Pydantic schema.
- **Validate all inputs**: Use Pydantic schemas to strictly enforce typing and input constraints.

---

## Security Rules

- **Never store passwords**: Always hash passwords using secure cryptographically strong algorithms (bcrypt/argon2).
- **Only `password_hash` is stored**: Passwords in their raw forms are processed in memory and immediately discarded.
- **JWT authentication only**: All authenticated state is stateless and signed using JWTs.
- **Role-Based Access Control (RBAC)**: Protect routes using decorators/dependencies checking user roles.

---

## Frontend Rules

- **Components must remain modular**: Break down complex UI views into cohesive subcomponents.
- **Feature-first folder organization**: Place logical UI structures inside feature folders (e.g., `auth`, `dashboard`, `endpoints`).
- **Shared UI components under `components/`**: Place buttons, inputs, inputs, and base layouts in root layout files.

---

## Agent Rules

- **Never communicate without authentication**: The agent must authenticate (via tokens or mutual TLS) before pushing telemetry.
- **All communication encrypted**: Standardize WebSockets over TLS (WSS) and HTTPS.
- **Agent logic remains independent**: Keep agent modules platform-independent where possible, separating platform specific system calls (Windows API) from telemetry payload logic.
