# Product Roadmap

This document outlines the milestones and sprint plans leading to the MVP release of Endpoint Sentinel X.

---

## Milestone 1: Project Foundation & Baseline

### Sprint 0: Foundation Setup (Completed)
- Clean up project file configurations.
- Standardize monorepo directory layout.
- Clean and update `.gitignore`.
- Set up python environment and virtualenv using `uv`.

### Sprint 1: Identity & Authorization (Completed)
- **Step 0**: Verify Neon database connectivity.
- **Step 1**: Implement Database & Identity models (organizations, users, roles) and generate the clean initial Alembic migration.
- **Step 2**: Implement User Authentication, JWT tokens, and login REST endpoints.
- **Step 3**: Integrate Role-Based Access Control (RBAC) middleware.

---

## Milestone 2: Telemetry Collection & Agent Communication

### Sprint 2: Agent Telemetry Collectors (Completed)
- Develop telemetry gatherers in Python Windows Agent (CPU, RAM, Disks, Network, OS details).
- Implement cache layer using SQLite/local files in agent for offline telemetry queueing.
- Standardize WebSocket payload structures in the `shared/` directory.

### Sprint 3: Realtime Streaming & Backend Processing (Completed)
- Set up async WebSocket server handling connection scaling.
- Implement message routing and ingestion services in the backend.
- Parse and persist endpoint telemetry to Neon PostgreSQL.
- Implement telemetry visualization endpoints.

---

## Milestone 3: Command Orchestration & UI Dashboard

### Sprint 4: Interactive Commands & Scripting (Completed)
- Create command execution schema.
- Develop interactive shell executor in Python Agent.
- Create WebSocket command routing interface.

### Sprint 5: UI Dashboard Development (Completed)
- Build frontend login, organization configuration, and monitoring view pages.
- Integrate charts (telemetry logs history) and system telemetry metrics tables.
- Implement real-time commands triggers.

---

## Milestone 4: Final Verification & MVP Release

### Sprint 6: Enterprise Security Center (Completed)
- Centralized security monitoring dashboard.
- Fleet security timeline and risk score engine.
- Persistent `SecurityEvent` audit logging pattern.
- Final stabilization and MVP Release (`1.0.0-rc1`).

---

## Milestone 5: Post-MVP Enterprise Capabilities

### Sprint 7: Automated Response Policies (Upcoming)
- Define `Policy` and `PolicyRule` schemas for automated evaluation.
- Integrate rule evaluation into `SecurityService` telemetry ingestion.
- Build Policy Management UI under `/policies`.
- Advanced Role-Based Access Control (RBAC) UI configuration.
