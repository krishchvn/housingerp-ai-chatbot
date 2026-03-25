# Repository Pattern

All database access goes through `backend/db/repositories/`. Routers and services never import `engine` or write raw SQL directly — they call repository functions.

---

## complaint_repo.py

### `insert_complaint(data: dict) → Optional[int]`
Inserts a new row into `ai_complaints`. Returns the generated `queriesComplaintId` or `None` on failure.

### `run_query(sql: str, user_id: int, society_id: int) → List[dict]`
Executes a validated LLM-generated SELECT query scoped to a user. Injects `:userId` and `:societyId` as bound parameters — the SQL string itself never has raw values.

### `enrich_complaint_rows(rows: List[dict]) → List[dict]`
Batch-replaces integer IDs with human-readable names. Uses a single `column_maps` dict — one entry per enrichable column:
```python
column_maps = {
    "createdby":           user_map,       # → "Aarav Sharma"
    "updatedby":           user_map,
    "userid":              user_map,
    "complaintcategoryid": cat_map,        # → "Water Issue"
    "status":              status_map,     # → "Opened"
}
```
Each lookup is a batch query (not N+1).

### `get_categories(society_id: int) → List[ComplaintCategory]`
Returns all active complaint categories for a society. Used to build the LLM classification prompt.

---

## user_repo.py

### `get_first_user() → Optional[User]`
Returns the first active user from `ai_users`. **Temporary** — will be replaced by session-based lookup after authentication is implemented.

### `get_user_by_name(name: str) → Optional[User]`
Looks up a user by first name, last name, or full name (case-insensitive). Used when a query mentions someone by name (e.g., "complaints by Aarav Sharma").

### `find_user_in_text(query: str) → Optional[User]` *(unused)*
Substring-scans all active users against query text. Removed from active use due to false positives (e.g., "Lee" matching "electricity"). Superseded by LLM `filter_type` classification.

---

## status_repo.py

Intentionally decoupled from complaints — importable by any future domain (billing, expenses, maintenance).

### `get_status_map(status_ids: List[int]) → Dict[int, str]`
Batch-fetches status names for a list of IDs. Returns `{0: "Opened", 1: "In Progress", ...}`.

### `get_all_statuses() → List[Dict]`
Returns all statuses as a list of `{statusId, statusName}` dicts. Useful for injecting into LLM prompts.
