# Database Schema

All tables live in a Supabase (PostgreSQL) instance. Schemas are defined in `backend/db/schemas/` and applied via `backend/db/run_schemas.py`.

---

## ai_complaints

Primary complaints table. One row per submitted complaint.

| Column | Type | Notes |
|--------|------|-------|
| `queriesComplaintId` | SERIAL PK | Auto-generated |
| `queriesComplaintGuid` | UUID | Client-side generated GUID |
| `reqNumber` | VARCHAR | Human-readable ref e.g. `REQ4C042F` |
| `societyId` | INTEGER | FK-like: scope to society |
| `buildingId` | INTEGER | |
| `flatId` | INTEGER | |
| `userId` | INTEGER | Resident who raised it |
| `createdBy` | INTEGER | Same as userId for self-service |
| `updatedBy` | INTEGER | |
| `complaintCategoryId` | INTEGER | FK → ai_complaint_categories |
| `subject` | VARCHAR | Short title (AI-generated) |
| `description` | TEXT | Detailed description (AI-generated) |
| `complaintComments` | TEXT | Original user text |
| `status` | INTEGER | FK → ai_status (0/1/2/3) |
| `process` | INTEGER | Internal workflow step |
| `userRating` | INTEGER | Post-resolution rating |
| `isActive` | BOOLEAN | Soft active flag |
| `isDeleted` | BOOLEAN | Soft delete |
| `aiClassifiedCategory` | VARCHAR | Category name string (redundant, for debug) |
| `aiConfidenceScore` | FLOAT | LLM confidence 0.0–1.0 |
| `aiRawInput` | TEXT | Original user message stored verbatim |
| `submittedViaChat` | BOOLEAN | True for all AI-submitted complaints |
| `createdOn` | TIMESTAMPTZ | |
| `updatedOn` | TIMESTAMPTZ | |

---

## ai_complaint_categories

Lookup table for complaint categories, scoped per society.

| Column | Type | Notes |
|--------|------|-------|
| `complaintCategoryId` | SERIAL PK | |
| `societyId` | INTEGER | Society scope |
| `complaintName` | VARCHAR | e.g. "Water Issue", "Cleaning Issue" |
| `isActive` | BOOLEAN | |

**Sample data:**
- Water Issue
- Light Issue
- Electricity Issue
- Cleaning Issue
- Fund Issues
- General Complaint

---

## ai_status

Lookup table for complaint status values.

| statusId | statusName |
|----------|------------|
| 0 | Opened |
| 1 | In Progress |
| 2 | Completed |
| 3 | Declined |

---

## ai_users

Residents registered in the AI module. Used for user context (no login implemented yet — first active user is fetched as the current user).

| Column | Type | Notes |
|--------|------|-------|
| `userId` | SERIAL PK | |
| `societyId` | INTEGER | |
| `buildingId` | INTEGER | |
| `flatId` | INTEGER | |
| `firstName` | VARCHAR | |
| `lastName` | VARCHAR | |
| `sex` | VARCHAR | |
| `status` | INTEGER | 1 = active |

---

## ai_chat_sessions / ai_chat_messages

Stores conversation history per session. **Not yet wired to the chat widget** — reserved for future multi-turn memory.

---

## ai_documents / ai_document_chunks

Reserved for Document Q&A feature. Stores uploaded documents and their vector-ready text chunks.

---

## ai_unanswered_questions

Logs questions the LLM could not answer. Used to identify gaps for future training/content.
