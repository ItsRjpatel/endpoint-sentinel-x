# Shared Monorepo Module

This folder contains shared structures, contracts, schemas, and configurations that are common between:
- The **Backend API** (FastAPI)
- The **Frontend App** (Vite + React)
- The **Agent** (Windows Python Service)

## Structure

- `/schemas/`: JSON schemas or protobuf files specifying telemetry message structure, command/control messages, and event structures.
- `/constants/`: Shared status codes, WebSocket codes, and routing parameters.

## Purpose

By decoupling schemas and protocol declarations from the backend core, we ensure consistency across the client, backend, and agent, preventing schema drift during rapid iterations.
