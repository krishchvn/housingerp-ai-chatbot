# API Reference — Complaints

Base path: `/complaints`

---

## POST /complaints

Convert plain-text input into a structured complaint and save it to the database.

### Request
```json
{ "text": "My tap has been leaking since morning" }
```

### Response `200`
```json
{
  "reqNumber": "REQEE0CB4",
  "category": "Water Issue",
  "categoryId": 1,
  "urgency": "medium",
  "subject": "Leaking Tap Since Morning",
  "description": "The tap in the apartment has been leaking since morning.",
  "confidence": 0.95,
  "savedToDb": true,
  "queriesComplaintId": 42,
  "needsClarification": false,
  "clarificationMessage": null
}
```

### Clarification Response (low confidence)
When the LLM confidence is below 0.4:
```json
{
  "reqNumber": "",
  "category": "",
  "categoryId": 0,
  "urgency": "",
  "subject": "",
  "description": "",
  "confidence": 0.1,
  "savedToDb": false,
  "needsClarification": true,
  "clarificationMessage": "I couldn't understand your complaint. Could you please describe the issue more clearly?"
}
```

### Error Responses
| Code | When |
|------|------|
| 404 | No active user found |
| 404 | No complaint categories found for society |
| 422 | LLM classification failed |

---

## POST /complaints/query

Convert a natural language question into SQL, execute it, and return enriched results.

### Request
```json
{ "query": "show all my open complaints" }
```

### Response `200`
```json
{
  "results": [
    {
      "reqnumber": "REQEE0CB4",
      "flatid": 101,
      "createdby": "Aarav Sharma",
      "updatedby": "Aarav Sharma",
      "complaintcategoryid": "Water Issue",
      "subject": "Leaking Tap Issue",
      "description": "Tap has been leaking since morning",
      "complaintcomments": "My tap has been leaking since morning",
      "queriescomplaintimage": null,
      "status": "Opened"
    }
  ],
  "count": 1,
  "message": "Found 1 complaint(s) for Aarav Sharma.",
  "sql": "SELECT * FROM ai_complaints WHERE userId = :userId AND societyId = :societyId AND status = 0"
}
```

### Filter Types

The LLM classifies each query into a `filter_type`. This determines how the router handles it:

| filter_type | Example query | Handling |
|-------------|--------------|----------|
| `user` | "complaints by Aarav Sharma" | Router looks up user by name, injects their `userId` |
| `category` | "show water issues" | SQL uses `complaintCategoryId = <id>` |
| `status` | "show open complaints" | SQL uses `status = 0` |
| `flatid` | "complaints for flat 201" | SQL uses `flatId = 201` |
| `buildingid` | "complaints for building 3" | SQL uses `buildingId = 3` |
| `subject` | "complaints about leaking" | SQL uses `LIKE` on `subject` |
| `null` | "show all my complaints" | No extra filter |

### Error Responses
| Code | When |
|------|------|
| 404 | No active user found |
| 404 | Named user not found in ai_users |
| 400 | SQL validation failed (non-SELECT, missing user scope) |
| 422 | LLM failed to parse query |
| 500 | Query execution failed |
