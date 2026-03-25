# Architecture Overview

## System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     Browser / Host App                   │
│                                                          │
│   ┌──────────────────────────────────────────────────┐  │
│   │              ChatWidget (React)                   │  │
│   │  Intent Detection → POST /complaints              │  │
│   │                   → POST /complaints/query        │  │
│   └──────────────────────┬───────────────────────────┘  │
└──────────────────────────┼──────────────────────────────┘
                           │ HTTP (Axios)
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                          │
│                                                          │
│   ┌─────────────┐    ┌──────────────────────────────┐   │
│   │   Routers   │───▶│         Services              │   │
│   │ complaints  │    │  classify_complaint()         │   │
│   │ chat        │    │  text_to_sql()                │   │
│   └─────────────┘    │  build_complaint_payload()    │   │
│                      └──────────────┬────────────────┘   │
│                                     │                     │
│   ┌─────────────────────────────────▼────────────────┐   │
│   │               Repositories                        │   │
│   │   complaint_repo  user_repo  status_repo          │   │
│   └─────────────────────────────────┬────────────────┘   │
└─────────────────────────────────────┼─────────────────────┘
                                      │ SQLAlchemy / psycopg2
                                      ▼
                           ┌──────────────────┐
                           │    Supabase       │
                           │   (PostgreSQL)    │
                           └──────────────────┘
                                      │
                           ┌──────────▼──────────┐
                           │    Groq LLM API      │
                           │  llama-3.3-70b       │
                           └─────────────────────┘
```

## Layer Responsibilities

| Layer | Files | Responsibility |
|-------|-------|----------------|
| **Routers** | `routers/*.py` | HTTP request parsing, response shaping, orchestration |
| **Services** | `services/*.py` | LLM calls, business logic, SQL validation |
| **Repositories** | `db/repositories/*.py` | All DB queries — one file per domain |
| **Models** | `models/*.py` | Pydantic schemas for requests, responses, internal types |
| **DB Connection** | `db/connection.py` | Single SQLAlchemy engine shared across all repos |

## Design Principles

- **Single Responsibility**: each layer does one thing; routers never talk to the DB directly.
- **Scalability**: adding a new domain (billing, expenses) = new files in each layer + one `include_router` line.
- **Safety**: LLM-generated SQL is never executed raw — always validated by `sql_validator.py` and scoped with `:userId` / `:societyId` placeholders.
- **Enrichment**: IDs stored in DB are enriched to human-readable names at the repository layer before returning to the router.
