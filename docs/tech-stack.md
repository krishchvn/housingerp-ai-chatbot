# Tech Stack

## Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11 | Runtime |
| FastAPI | 0.110+ | HTTP framework — async, auto-docs via OpenAPI |
| Uvicorn | latest | ASGI server |
| Pydantic v2 | 2.x | Request/response validation and serialisation |
| SQLAlchemy | 2.0 (sync) | SQL query builder and connection pooling |
| psycopg2-binary | 2.x | PostgreSQL driver |
| LangChain Core | latest | LLM message abstractions |
| langchain-groq | latest | Groq LLM client integration |
| python-dotenv | latest | `.env` file loading |

### LLM

| Item | Value |
|------|-------|
| Provider | Groq |
| Model | `llama-3.3-70b-versatile` (configurable via `GROQ_MODEL` env var) |
| Temperature | 0 (deterministic output) |
| Usage | Complaint classification (text → JSON) and NL → SQL |

### Why Groq?
Low-latency inference on open-weight models. Llama 3.3 70B provides high accuracy for structured JSON output tasks.

---

## Database

| Technology | Purpose |
|------------|---------|
| Supabase | Hosted PostgreSQL — managed DB with dashboard |
| PostgreSQL | Relational DB for all structured data |

Tables: `ai_complaints`, `ai_complaint_categories`, `ai_users`, `ai_status`,
`ai_chat_sessions`, `ai_chat_messages`, `ai_unanswered_questions`,
`ai_documents`, `ai_document_chunks`

---

## Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18 | UI framework |
| TypeScript | 5.x | Type safety |
| Vite | 5.x | Build tool and dev server |
| Axios | 1.x | HTTP client with error handling |

### No external UI library
All styling is inline `React.CSSProperties` — zero CSS dependencies, fully portable as an embeddable widget.

---

## Dev Tooling

| Tool | Purpose |
|------|---------|
| ESLint | TypeScript linting |
| python-dotenv | Environment config |
| Uvicorn `--reload` | Hot reload during development |
| Vite HMR | Hot Module Replacement for frontend |
