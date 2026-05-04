# Frontend Architecture

## Stack

React 18 + TypeScript + Vite. Zero external UI libraries — all styling is inline `React.CSSProperties`.

## Folder Structure

```
frontend/src/
├── main.tsx          # ReactDOM.createRoot entry
├── App.tsx           # Root: dark page + <ChatWidget />
├── ChatWidget.tsx    # Entire chat experience (single file)
└── assets/
```

## ChatWidget.tsx — Component Breakdown

```
ChatWidget (stateful)
├── State
│   ├── open: boolean              — widget open/closed
│   ├── messages: Message[]        — chat history
│   ├── input: string              — current text field value
│   └── loading: boolean           — disables input during API call
│
├── Intent Detection
│   └── detectIntent(text) → "complaint" | "query"
│       Keyword-based: checks against QUERY_KEYWORDS list
│
├── API Routing (sendMessage)
│   ├── "query"     → POST /complaints/query
│   └── "complaint" → POST /complaints
│
├── Sub-components
│   ├── Bubble         — renders a single message (user, assistant, error, complaint card, query table)
│   ├── ComplaintCard  — structured card for a newly created complaint
│   └── QueryResultCard — table of query results with column whitelist
│
└── Styles
    ├── styles{}     — layout: FAB, window, header, messages, input row
    └── cardStyles{} — ComplaintCard and QueryResultCard visual styles
```

## Message Type System

```typescript
interface Message {
  role: "user" | "assistant";
  type: "text" | "complaint" | "query" | "error";
  text?: string;
  complaint?: ComplaintCreatedData;
  query?: QueryResultData;
}
```

Each `type` renders a different UI in `<Bubble>`:
- `text` — plain chat bubble
- `complaint` — `<ComplaintCard>` with urgency badge, category, req number
- `query` — `<QueryResultCard>` table
- `error` — red error bubble

## Query Result Table

Columns are filtered to a whitelist (`COMPLAINT_VISIBLE_COLUMNS`) and labels are remapped via `COLUMN_LABELS`:
```typescript
const COMPLAINT_VISIBLE_COLUMNS = [
  "reqnumber", "flatid", "createdby", "updatedby", "complaintcategoryid",
  "subject", "description", "complaintcomments", "queriescomplaintimage", "status",
];
const COLUMN_LABELS = { complaintcategoryid: "complaintcategory" };
```

## Environment Variable

| Variable | Default | Purpose |
|----------|---------|---------|
| `VITE_API_BASE` | `https://housingerp-ai-chatbot.onrender.com` | Backend base URL |
