# Security Notes

This document provides an overview of the security architecture, current implementations, and planned enhancements for **Endpoint Sentinel X**.

---

## 1. Current Hashing Implementation
- **Algorithm**: `bcrypt` (administered via `passlib.context.CryptContext`).
- **Compatibility Pinning**: We explicitly pin `bcrypt==4.0.1` to maintain native compatibility with the `passlib` wrapper. This avoids initialization errors (`AttributeError` for `__about__` metadata and `ValueError` for long input strings) associated with unpatched `passlib` dynamic loading under modern `bcrypt` releases.

---

## 2. JWT Authentication Overview
- **Signing Key**: Sourced dynamically from environment settings (`JWT_SECRET_KEY`).
- **Signing Algorithm**: `HS256` (HMAC with SHA-256).
- **Access Tokens**: Short-lived (30 minutes duration). Contains payload details including the user's external UUID (`sub`) and token type (`"type": "access"`).
- **Validation**: Enforced via FastAPI dependencies (`get_current_user` and `get_current_active_user`).

---

## 3. Refresh Token Design
- **Lifespan**: Long-lived (7 days duration).
- **Format**: JWT containing user UUID (`sub`) and token type (`"type": "refresh"`).
- **Lifecycle**: Used exclusively at `POST /api/v1/auth/refresh` to request a new token pair. If a refresh token is expired or altered, authentication fails with a `401 Unauthorized`.

---

## 4. Current Logout Behavior (Stateless)
- **Mechanics**: The endpoint `POST /api/v1/auth/logout` is completely stateless. It accepts the client's token and responds with a success message.
- **Client Handling**: The client application is responsible for discarding the access and refresh tokens from memory. The server does not maintain server-side invalidation lists in this sprint.

---

## 5. Planned Future Improvements
To support 10,000+ endpoints and strict enterprise compliance, the security layer is scheduled to transition to:
* **Argon2id Hashing**: Migrate from legacy bcrypt to Argon2id (OWASP recommendation) via `argon2-cffi` to prevent password length limits (72 bytes) and defend against GPU-based cracking.
* **Redis Token Blacklist**: Track active token invalidations on `/logout` in a fast Redis cache with Time-To-Live (TTL) expiration matching token lifespans.
* **Refresh Token Rotation (RTR)**: Revoke the current refresh token and return a new one on every refresh cycle. Replaying an old refresh token will trigger automatic session termination for the user.
* **Session Management**: Maintain active session mappings in Redis to enable administrators to list active user locations and revoke compromised sessions instantly.
