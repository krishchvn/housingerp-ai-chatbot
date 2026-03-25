# HousingERP AI — Documentation Index

## Contents

| Section | Description |
|---------|-------------|
| [Tech Stack](./tech-stack.md) | All technologies, libraries, and why they were chosen |
| [Architecture](./architecture/overview.md) | System design and layer responsibilities |
| [Database](./database/schema.md) | Tables, columns, and repository pattern |
| [API Reference](./api/complaints.md) | All HTTP endpoints with request/response shapes |
| [Data Flows](./flows/complaint-creation.md) | Step-by-step flows for every feature |
| [Services](./services/complaint-service.md) | Business logic and LLM integration details |
| [Frontend](./frontend/components.md) | React components and intent detection |
| [Scenarios](./scenarios/covered.md) | All supported query and complaint scenarios |

## Adding a New Domain (e.g. Billing, Expenses)

The architecture is intentionally layered so adding a new domain requires:

1. `backend/models/<domain>.py` — Pydantic request/response models
2. `backend/db/repositories/<domain>_repo.py` — DB queries
3. `backend/services/<domain>_service.py` — LLM prompts + business logic
4. `backend/routers/<domain>.py` — FastAPI router
5. Register in `backend/main.py`: `app.include_router(<domain>_router)`
6. `docs/api/<domain>.md`, `docs/flows/<domain>-*.md` — Documentation
