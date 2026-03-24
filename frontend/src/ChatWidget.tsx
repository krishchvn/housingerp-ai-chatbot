import { useState, useRef, useEffect } from "react";
import axios from "axios";

// ── Types ────────────────────────────────────────────────────────────────────

interface Message {
  role: "user" | "assistant";
  content: string;
  intent?: string;
  requiresConfirmation?: boolean;
}

interface ChatRequest {
  message: string;
  sessionId?: string;
  userId: number;
  societyId: number;
  buildingId?: number;
  flatId?: number;
  authToken: string;
}

interface ChatResponse {
  reply: string;
  intent: string;
  sessionId: string;
  complaintDraft?: Record<string, unknown>;
  requiresConfirmation: boolean;
}

// ── Props — pass in from your app's auth context ─────────────────────────────

interface ChatWidgetProps {
  userId: number;
  societyId: number;
  buildingId?: number;
  flatId?: number;
  authToken: string;
}

const API_BASE = import.meta.env.VITE_CHATBOT_API ?? "http://localhost:8000";

export default function ChatWidget({
  userId,
  societyId,
  buildingId,
  flatId,
  authToken,
}: ChatWidgetProps) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hi! I'm your society assistant. I can help you raise complaints or answer questions about society rules. How can I help?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text?: string) => {
    const messageText = text ?? input.trim();
    if (!messageText || loading) return;

    const userMsg: Message = { role: "user", content: messageText };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const payload: ChatRequest = {
        message: messageText,
        sessionId,
        userId,
        societyId,
        buildingId,
        flatId,
        authToken,
      };

      const { data } = await axios.post<ChatResponse>(`${API_BASE}/chat`, payload);

      setSessionId(data.sessionId);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.reply,
          intent: data.intent,
          requiresConfirmation: data.requiresConfirmation,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const lastMsg = messages[messages.length - 1];
  const showConfirmButtons = lastMsg?.requiresConfirmation && lastMsg?.role === "assistant";

  return (
    <div>
      {/* Floating button */}
      <button
        onClick={() => setOpen((o) => !o)}
        style={styles.fab}
        title="Society Assistant"
      >
        {open ? "✕" : "💬"}
      </button>

      {/* Chat window */}
      {open && (
        <div style={styles.window}>
          {/* Header */}
          <div style={styles.header}>
            <span>🏠 Society Assistant</span>
            <button onClick={() => setOpen(false)} style={styles.closeBtn}>✕</button>
          </div>

          {/* Messages */}
          <div style={styles.messages}>
            {messages.map((msg, i) => (
              <div
                key={i}
                style={{
                  ...styles.bubble,
                  alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
                  background: msg.role === "user" ? "#22c55e" : "#1e293b",
                  color: "#fff",
                }}
              >
                {/* Render newlines and bold */}
                {msg.content.split("\n").map((line, j) => (
                  <span key={j}>
                    {line.split(/\*\*(.*?)\*\*/g).map((part, k) =>
                      k % 2 === 1 ? <strong key={k}>{part}</strong> : part
                    )}
                    <br />
                  </span>
                ))}
              </div>
            ))}

            {loading && (
              <div style={{ ...styles.bubble, alignSelf: "flex-start", background: "#1e293b", color: "#94a3b8" }}>
                Typing...
              </div>
            )}

            {/* Yes/No quick replies for complaint confirmation */}
            {showConfirmButtons && !loading && (
              <div style={styles.quickReplies}>
                <button style={styles.yesBtn} onClick={() => sendMessage("Yes")}>✅ Yes, submit</button>
                <button style={styles.noBtn} onClick={() => sendMessage("No")}>❌ Cancel</button>
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
              placeholder="Type your message..."
              disabled={loading}
            />
            <button
              style={styles.sendBtn}
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
            >
              ➤
            </button>
          </div>
        </div>
      )}
      <div />
      );
}

      // ── Inline styles (replace with Tailwind/CSS if preferred) ───────────────────

      const styles: Record<string, React.CSSProperties> = {
        fab: {
        position: "fixed",
      bottom: 24,
      right: 24,
      width: 56,
      height: 56,
      borderRadius: "50%",
      background: "#22c55e",
      border: "none",
      fontSize: 24,
      cursor: "pointer",
      boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
      zIndex: 9999,
  },
      window: {
        position: "fixed",
      bottom: 92,
      right: 24,
      width: 360,
      height: 520,
      background: "#0f172a",
      borderRadius: 12,
      boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
      display: "flex",
      flexDirection: "column",
      zIndex: 9998,
      overflow: "hidden",
  },
      header: {
        background: "#1e293b",
      padding: "12px 16px",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      color: "#fff",
      fontWeight: 600,
      fontSize: 14,
  },
      closeBtn: {
        background: "none",
      border: "none",
      color: "#94a3b8",
      cursor: "pointer",
      fontSize: 16,
  },
      messages: {
        flex: 1,
      overflowY: "auto",
      padding: 12,
      display: "flex",
      flexDirection: "column",
      gap: 8,
  },
      bubble: {
        maxWidth: "80%",
      padding: "8px 12px",
      borderRadius: 10,
      fontSize: 13,
      lineHeight: 1.5,
  },
      quickReplies: {
        display: "flex",
      gap: 8,
      alignSelf: "flex-start",
  },
      yesBtn: {
        padding: "6px 14px",
      borderRadius: 8,
      background: "#22c55e",
      border: "none",
      color: "#fff",
      cursor: "pointer",
      fontSize: 12,
  },
      noBtn: {
        padding: "6px 14px",
      borderRadius: 8,
      background: "#ef4444",
      border: "none",
      color: "#fff",
      cursor: "pointer",
      fontSize: 12,
  },
      inputRow: {
        display: "flex",
      padding: "8px 12px",
      gap: 8,
      borderTop: "1px solid #1e293b",
  },
      input: {
        flex: 1,
      background: "#1e293b",
      border: "1px solid #334155",
      borderRadius: 8,
      padding: "8px 12px",
      color: "#fff",
      fontSize: 13,
      outline: "none",
  },
      sendBtn: {
        background: "#22c55e",
      border: "none",
      borderRadius: 8,
      padding: "8px 14px",
      color: "#fff",
      cursor: "pointer",
      fontSize: 16,
  },
};
