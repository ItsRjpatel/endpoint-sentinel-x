# Endpoint Sentinel X

Endpoint Sentinel X (ESX) is a cloud-native, enterprise-grade Endpoint Monitoring & Management Platform designed for scale, maintainability, and security. It is built to monitor and manage 10,000+ endpoints.

## Vision

To provide real-time, lightweight, secure, and highly scalable endpoint telemetry collection and centralized policy enforcement. ESX aims to help system administrators and security analysts observe, analyze, and command enterprise endpoints from a single pane of glass.

## Architecture

ESX follows **Clean/Hexagonal Architecture** principles:
- **Domain Layer**: Contains enterprise entities, values, and domain exceptions (completely framework-independent).
- **Application Layer**: Contains command/query handlers representing business flows.
- **Infrastructure Layer**: Technical components such as database session configurations, caches (Redis), and communication logic.
- **API/Presentation Layer**: REST routers and WebSocket hubs presenting endpoints to clients and agents.

---

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy 2.0 (Async), Alembic, Pydantic v2, JWT, WebSockets, AsyncIO, Neon PostgreSQL, Redis, Python 3.13+.
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, shadcn/ui, TanStack Query, Recharts, React Router.
- **Agent**: Windows Python Service.
- **Package Management**: `uv` for Python (backend & agent), `npm` for Node.js (frontend).

---

## Folder Structure

```
endpoint-sentinel-x/
├── agent/                     # Windows agent service skeleton
├── backend/                   # FastAPI Application
├── docs/                      # Standard product decisions & specs
├── frontend/                  # React dashboard frontend
├── shared/                    # Shared schemas, constants, and events
└── infrastructure/            # Orchestration configs & docker-compose
```

---

## Development Workflow

1. **Local Setup**: Set up virtual environments using `uv`.
2. **Coding Standards**: Adhere to linting rules checked via Ruff.
3. **Database Changes**: Generate Alembic migrations for any model changes.
4. **Testing**: Write unit and integration tests and verify using Pytest.

---

## Installation & Running

### Prerequisites
- Python 3.13+
- Node.js 18+
- Docker & Docker Compose
- `uv` installed (`pip install uv` or native installer)

---

### Running Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Synchronize environment and virtual environment:
   ```bash
   uv sync
   ```
3. Run FastAPI using Uvicorn:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

---

### Running Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

---

### Running Agent

1. Navigate to the agent directory:
   ```bash
   cd agent
   ```
2. Synchronize packages:
   ```bash
   uv sync
   ```
3. Run the agent core loop:
   ```bash
   uv run python main.py
   ```

---

## Database Migrations

Database migrations are managed via Alembic.

- Generate a new migration:
  ```bash
  uv run alembic revision --autogenerate -m "description"
  ```
- Apply migrations:
  ```bash
  uv run alembic upgrade head
  ```
- Revert the last migration:
  ```bash
  uv run alembic downgrade -1
  ```

---

## Code Quality

We use Ruff for linting and formatting.

- Run linter checks:
  ```bash
  uv run ruff check .
  ```
- Run formatter checks:
  ```bash
  uv run ruff format --check .
  ```

---

## Testing

Tests are run using Pytest.

- Run tests in backend:
  ```bash
  cd backend
  uv run pytest
  ```

---

## Roadmap

Milestones and release timelines are outlined in [ROADMAP.md](file:///d:/New%20Start/endpoint-sentinel-x/ROADMAP.md).

---

## License

This project is licensed under the MIT License.
