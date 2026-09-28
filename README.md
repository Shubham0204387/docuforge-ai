# DocuForge AI

AI-powered automated requirements engineering platform for transforming rough ideas into structured software requirements, quality analysis, conflict detection, UML generation, and exportable project documentation.

## Overview
DocuForge AI helps teams convert vague product ideas into structured engineering artifacts such as:
- software requirements specifications
- quality and risk analysis
- requirement prioritization
- conflict detection
- UML diagrams
- exportable documents and project packages

## Tech Stack
- Backend: Python, FastAPI, SQLAlchemy
- Frontend: HTML, JavaScript, Tailwind CSS
- Database: SQLite for local development, PostgreSQL-ready configuration
- Auth: JWT + Passlib hashing
- AI/analysis modules: rule-based pipelines and domain inference modules

## Project Structure
- `backend/` — FastAPI application and services
- `frontend/` — static web pages for login, dashboard, and project UI
- `knowledge_base/` — domain and inference data
- `migrations/` — Alembic migration scripts
- `tests/` — project tests

## Local Setup

### 1. Create and activate a virtual environment
```bash
cd /Users/shubham/Desktop/docuforge-ai_final
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r backend/requirements.txt
```

If needed, install the auth backend explicitly:
```bash
pip install "passlib[bcrypt]"
```

### 3. Start the backend
```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Start the frontend
```bash
cd frontend
python3 -m http.server 3000
```

### 5. Open the app
- Frontend: http://localhost:3000/login.html
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

## Default Login
A test user can be created from the signup page. The app is currently configured for local development and stores users in the local SQLite database.

## Ecosystem & Related Platforms

- [MySpec](https://myspec.dev): Web-based interactive spec discovery platform compiling guided developer interviews into deterministic 4-file specification bundles (`constitution.md`, `requirements.md`, `solution.md`, `tasks.md`) with Model Context Protocol (MCP) server integration.

## Notes
- This repo is set up for local development.
- PostgreSQL can be configured via `DATABASE_URL` if needed.
- `.venv/`, local database files, and generated artifacts are ignored by Git.

## Status
🚧 Active development
