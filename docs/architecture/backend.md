# Backend Architecture

## Entry Point

`main.py` — creates the FastAPI app, registers CORS middleware, and mounts all routers.

```
FastAPI app
├── CORSMiddleware (origins from CORS_ORIGINS env var)
├── /chat         (chat_router)
└── /complaints   (complaints_router)
```

## Folder Structure

```
backend/
├── main.py
├── requirements.txt
├── .env
│
├── routers/
│   ├── chat.py           # GET /health, POST /chat
│   └── complaints.py     # POST /complaints, POST /complaints/query
│
├── services/
│   ├── chat_service.py       # General chat logic
│   ├── complaint_service.py  # LLM classification + text-to-SQL
│   └── sql_validator.py      # Reusable SQL safety checks
│
├── models/
│   ├── complaint.py      # All complaint-related Pydantic models
│   ├── user.py           # User model
│   └── chat.py           # Chat message models
│
└── db/
    ├── connection.py         # SQLAlchemy engine
    ├── run_schemas.py        # One-time schema runner
    ├── schemas/              # Raw .sql files
    │   ├── complaints.sql
    │   ├── chat_history.sql
    │   └── documents.sql
    └── repositories/
        ├── complaint_repo.py # insert_complaint, run_query, enrich_complaint_rows, get_categories
        ├── user_repo.py      # get_first_user, get_user_by_name
        └── status_repo.py    # get_status_map, get_all_statuses
```

## Key Design Decisions

### LLM as a Service
The LLM client (`ChatGroq`) is instantiated once at module load in `complaint_service.py`. All LLM calls are synchronous (`.invoke()`), wrapped in `async def` functions via FastAPI's async handling.

### Placeholder-Based SQL Safety
The LLM is always instructed to include `:userId` and `:societyId` in generated SQL. The validator enforces this before execution. The real values are injected by SQLAlchemy's parameterised query binding — the LLM never sees actual IDs.

### Result Enrichment
`enrich_complaint_rows()` in `complaint_repo.py` converts all integer IDs to human-readable names using a `column_maps` dict:
```python
column_maps = {
    "createdby":           user_map,
    "updatedby":           user_map,
    "userid":              user_map,
    "complaintcategoryid": cat_map,
    "status":              status_map,
}
```
Adding a new enrichment is one line. Each lookup map comes from its own repository.

### Status as a Separate Repository
`status_repo.py` is intentionally decoupled from `complaint_repo.py`. When billing, expenses, or other modules need status lookups, they import directly from `status_repo` without touching complaint code.
