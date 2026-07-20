# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-07-21

### Added
- Created abstract `BaseEntity` with primary key `id` (integer) and `uuid` (UUID4) fields.
- Implemented core identity models `Organization` and `User` with a one-to-many relationship mapping.
- Added string-backed `UserRole` enum.
- Created `OrganizationCreate`, `OrganizationUpdate`, and `OrganizationResponse` Pydantic schemas.
- Created `UserCreate`, `UserUpdate`, and `UserResponse` Pydantic schemas.
- Implemented `OrganizationRepository` and `UserRepository` providing basic CRUD operations.
- Added `OrganizationService` and `UserService` skeleton interfaces.
- Generated and executed a clean baseline Alembic migration (`33232f9d6499`) on Neon PostgreSQL.

### Changed
- Standardized directory layout to separate `backend`, `frontend`, `agent`, `shared`, `docs`, and `infrastructure` modules.
- Refactored `backend/app/core/config.py` validator to map database URL options dynamically (`sslmode` -> `ssl`) and strip unsupported options (`channel_binding`), enabling direct compatibility with `asyncpg`.
- Configured Pydantic Settings to load the env file `.env.backend` dynamically.
- Standardized and updated root `.gitignore` parameters.

### Removed
- Deleted the previous identity migration `fcb49f9e2594` to enable a clean initial baseline.
- Deleted duplicate dependency configurations (`backend/requirements.txt`).
