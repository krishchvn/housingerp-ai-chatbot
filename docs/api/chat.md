# API Reference — Chat

Base path: `/`

---

## GET /health

Health check endpoint.

### Response `200`
```json
{ "status": "ok" }
```

---

## POST /chat

General-purpose chat endpoint (future use). Currently available but the main complaint flows go through `/complaints`.

### Request
```json
{ "message": "Hello" }
```

### Response `200`
```json
{ "reply": "..." }
```

---

## Notes

The chat router is separate from the complaints router so that future features (Document Q&A, general assistant) can be added to `routers/chat.py` without touching complaint logic.
