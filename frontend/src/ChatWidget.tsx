import { useState, useRef, useEffect } from "react";
import axios from "axios";

// ── Types ─────────────────────────────────────────────────────────────────────

interface ComplaintCreatedData {
  reqNumber: string;
  category: string;
  urgency: string;
  subject: string;
  description: string;
  confidence: number;
  savedToDb: boolean;
}

interface QueryResultData {
  results: Record<string, unknown>[];
  count: number;
  message: string;
}

interface Message {
  role: "user" | "assistant";
  text?: string;
  type: "text" | "complaint" | "query" | "error";
  complaint?: ComplaintCreatedData;
  query?: QueryResultData;
}

// ── Constants ─────────────────────────────────────────────────────────────────

const API_BASE = import.meta.env.VITE_API_BASE ?? "https://housingerp-ai-chatbot.onrender.com";

const COLUMN_LABELS: Record<string, string> = {
  complaintcategoryid: "complaintcategory",
};

const COMPLAINT_VISIBLE_COLUMNS = [
  "reqnumber", "flatid", "createdby", "updatedby", "complaintcategoryid",
  "subject", "description", "complaintcomments", "queriescomplaintimage", "status",
];

const QUERY_KEYWORDS = [
  "show", "list", "get", "find", "what", "how many",
  "status", "tell me", "recent", "open", "resolved", "latest", "display",
  "give me", "all complaints", "complaints by", "complaints with",
  "complaints for", "fetch", "retrieve",
];

const URGENCY_COLORS: Record<string, string> = {
  low: "#22c55e",
  medium: "#f59e0b",
  high: "#ef4444",
  critical: "#7c3aed",
};

// ── Intent detection ──────────────────────────────────────────────────────────

function detectIntent(text: string): "complaint" | "query" {
  const lower = text.toLowerCase();
  return QUERY_KEYWORDS.some((k) => lower.includes(k)) ? "query" : "complaint";
}

// ── Subcomponents ─────────────────────────────────────────────────────────────

function ComplaintCard({ data }: { data: ComplaintCreatedData }) {
  const color = URGENCY_COLORS[data.urgency] ?? "#64748b";
  return (
    <div style={cardStyles.card}>
      <div style={{ ...cardStyles.badge, background: color }}>{data.urgency.toUpperCase()}</div>
      <div style={cardStyles.row}><span style={cardStyles.label}>Category</span><span>{data.category}</span></div>
      <div style={cardStyles.row}><span style={cardStyles.label}>Subject</span><span>{data.subject}</span></div>
      <div style={cardStyles.row}><span style={cardStyles.label}>Req No.</span><span style={cardStyles.reqNum}>{data.reqNumber}</span></div>
      <div style={cardStyles.row}><span style={cardStyles.label}>Description</span><span style={{ color: "#94a3b8", fontSize: 12 }}>{data.description}</span></div>
      <div style={{ ...cardStyles.status, color: data.savedToDb ? "#22c55e" : "#ef4444" }}>
        {data.savedToDb ? "✓ Saved to database" : "⚠ Not saved"}
      </div>
    </div>
  );
}

function QueryResultCard({ data }: { data: QueryResultData }) {
  if (data.count === 0) {
    return <div style={cardStyles.empty}>{data.message}</div>;
  }

  const allColumns = Object.keys(data.results[0]);
  const columns = allColumns.filter((c) =>
    COMPLAINT_VISIBLE_COLUMNS.includes(c.toLowerCase())
  );

  return (
    <div style={cardStyles.queryWrap}>
      <div style={cardStyles.queryMeta}>{data.message}</div>
      <div style={cardStyles.tableWrapper}>
        <table style={cardStyles.table}>
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col} style={cardStyles.th}>{COLUMN_LABELS[col] ?? col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.results.map((row, i) => (
              <tr key={i} style={i % 2 === 0 ? cardStyles.trEven : cardStyles.trOdd}>
                {columns.map((col) => (
                  <td key={col} style={cardStyles.td}>{String(row[col] ?? "—")}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Bubble({ msg }: { msg: Message }) {
  const isUser = msg.role === "user";
  if (isUser) {
    return (
      <div style={{ ...styles.bubble, alignSelf: "flex-end", background: "#22c55e", color: "#fff" }}>
        {msg.text}
      </div>
    );
  }

  if (msg.type === "error") {
    return (
      <div style={{ ...styles.bubble, alignSelf: "flex-start", background: "#450a0a", color: "#fca5a5" }}>
        {msg.text}
      </div>
    );
  }

  if (msg.type === "complaint" && msg.complaint) {
    return (
      <div style={{ alignSelf: "flex-start", maxWidth: "90%" }}>
        <div style={{ ...styles.bubble, background: "#1e293b", color: "#94a3b8", marginBottom: 6 }}>
          Got it! Here's your complaint:
        </div>
        <ComplaintCard data={msg.complaint} />
      </div>
    );
  }

  if (msg.type === "query" && msg.query) {
    return (
      <div style={{ alignSelf: "flex-start", maxWidth: "90%" }}>
        <QueryResultCard data={msg.query} />
      </div>
    );
  }

  return (
    <div style={{ ...styles.bubble, alignSelf: "flex-start", background: "#1e293b", color: "#e2e8f0" }}>
      {msg.text}
    </div>
  );
}

// ── Main widget ───────────────────────────────────────────────────────────────

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      type: "text",
      text: "Hi! I'm your society assistant. Describe an issue to raise a complaint, or ask me to show your complaints.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const addMessage = (msg: Message) => setMessages((prev) => [...prev, msg]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    addMessage({ role: "user", type: "text", text });
    setInput("");
    setLoading(true);

    const intent = detectIntent(text);

    try {
      if (intent === "query") {
        const { data } = await axios.post(`${API_BASE}/complaints/query`, { query: text });
        addMessage({
          role: "assistant",
          type: "query",
          query: { results: data.results, count: data.count, message: data.message },
        });
      } else {
        const { data } = await axios.post(`${API_BASE}/complaints`, { text });
        if (data.needsClarification) {
          addMessage({
            role: "assistant",
            type: "text",
            text: data.clarificationMessage ?? "Could you please describe your issue more clearly?",
          });
        } else {
          addMessage({
            role: "assistant",
            type: "complaint",
            complaint: {
              reqNumber: data.reqNumber,
              category: data.category,
              urgency: data.urgency,
              subject: data.subject,
              description: data.description,
              confidence: data.confidence,
              savedToDb: data.savedToDb,
            },
          });
        }
      }
    } catch (err: unknown) {
      const message =
        axios.isAxiosError(err)
          ? err.response?.data?.detail ?? "Something went wrong."
          : "Something went wrong.";
      addMessage({ role: "assistant", type: "error", text: message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating button */}
      <button onClick={() => setOpen((o) => !o)} style={styles.fab} title="Society Assistant">
        {open ? "✕" : "💬"}
      </button>

      {open && (
        <div style={styles.window}>
          {/* Header */}
          <div style={styles.header}>
            <span>🏠 Society Assistant</span>
            <button onClick={() => setOpen(false)} style={styles.closeBtn}>✕</button>
          </div>

          {/* Messages */}
          <div style={styles.messages}>
            {messages.map((msg, i) => <Bubble key={i} msg={msg} />)}
            {loading && (
              <div style={{ ...styles.bubble, alignSelf: "flex-start", background: "#1e293b", color: "#475569" }}>
                Thinking...
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div style={styles.inputRow}>
            <input
              style={styles.input}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder="Describe an issue or ask about complaints..."
              disabled={loading}
            />
            <button style={styles.sendBtn} onClick={sendMessage} disabled={loading || !input.trim()}>
              ➤
            </button>
          </div>
        </div>
      )}
    </>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────

const styles: Record<string, React.CSSProperties> = {
  fab: {
    position: "fixed", bottom: 24, right: 24,
    width: 56, height: 56, borderRadius: "50%",
    background: "#22c55e", border: "none",
    fontSize: 24, cursor: "pointer",
    boxShadow: "0 4px 12px rgba(0,0,0,0.3)", zIndex: 9999,
  },
  window: {
    position: "fixed", bottom: 92, right: 24,
    width: 520, height: 560,
    background: "#0f172a", borderRadius: 12,
    boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
    display: "flex", flexDirection: "column",
    zIndex: 9998, overflow: "hidden",
  },
  header: {
    background: "#1e293b", padding: "12px 16px",
    display: "flex", justifyContent: "space-between", alignItems: "center",
    color: "#fff", fontWeight: 600, fontSize: 14,
  },
  closeBtn: { background: "none", border: "none", color: "#94a3b8", cursor: "pointer", fontSize: 16 },
  messages: {
    flex: 1, overflowY: "auto", padding: 12,
    display: "flex", flexDirection: "column", gap: 8,
  },
  bubble: {
    maxWidth: "80%", padding: "8px 12px",
    borderRadius: 10, fontSize: 13, lineHeight: 1.5,
  },
  inputRow: { display: "flex", padding: "8px 12px", gap: 8, borderTop: "1px solid #1e293b" },
  input: {
    flex: 1, background: "#1e293b", border: "1px solid #334155",
    borderRadius: 8, padding: "8px 12px", color: "#fff", fontSize: 13, outline: "none",
  },
  sendBtn: {
    background: "#22c55e", border: "none", borderRadius: 8,
    padding: "8px 14px", color: "#fff", cursor: "pointer", fontSize: 16,
  },
};

const cardStyles: Record<string, React.CSSProperties> = {
  card: {
    background: "#1e293b", borderRadius: 10, padding: 12,
    fontSize: 13, display: "flex", flexDirection: "column", gap: 6, minWidth: 260,
  },
  badge: {
    alignSelf: "flex-start", borderRadius: 4, padding: "2px 8px",
    fontSize: 11, fontWeight: 700, color: "#fff", marginBottom: 4,
  },
  row: { display: "flex", flexDirection: "column", gap: 2 },
  label: { fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em" },
  reqNum: { color: "#22c55e", fontWeight: 700, fontFamily: "monospace" },
  status: { fontSize: 11, marginTop: 4 },
  empty: {
    background: "#1e293b", borderRadius: 10, padding: "10px 14px",
    color: "#64748b", fontSize: 13,
  },
  queryWrap: { display: "flex", flexDirection: "column", gap: 6 },
  queryMeta: { color: "#94a3b8", fontSize: 12, marginBottom: 4 },
  tableWrapper: { overflowX: "auto", borderRadius: 8, border: "1px solid #334155" },
  table: { borderCollapse: "collapse", width: "100%", fontSize: 12 },
  th: {
    background: "#1e293b", color: "#94a3b8", padding: "6px 10px",
    textAlign: "left", fontWeight: 600, whiteSpace: "nowrap",
    borderBottom: "1px solid #334155",
  },
  td: { padding: "6px 10px", color: "#e2e8f0", whiteSpace: "nowrap", borderBottom: "1px solid #1e293b" },
  trEven: { background: "#0f172a" },
  trOdd: { background: "#111827" },
};
