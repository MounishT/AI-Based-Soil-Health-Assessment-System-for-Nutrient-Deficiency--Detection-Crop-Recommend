"use client";
import { useState, useRef, useEffect } from "react";
import { MessageCircle, X, Send } from "lucide-react";
import { useTranslation } from "react-i18next";

export default function ChatWidget() {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "bot", content: "Hello! I'm your farming assistant. Ask me about fertilizers, crops, pests, or irrigation." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text) => {
    const msg = text || input.trim();
    if (!msg) return;
    setInput("");
    setMessages((p) => [...p, { role: "user", content: msg }]);
    setLoading(true);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: msg }) });
      const data = await res.json();
      setMessages((p) => [...p, { role: "bot", content: data.reply }]);
      if (data.suggestions?.length) setMessages((p) => [...p, { role: "suggestions", items: data.suggestions }]);
    } catch {
      setMessages((p) => [...p, { role: "bot", content: "Sorry, I couldn't reach the server." }]);
    } finally { setLoading(false); }
  };

  return (
    <>
      <button onClick={() => setOpen(!open)}
        style={{ position: "fixed", bottom: "80px", right: "20px", zIndex: 999, backgroundColor: "#4caf50", color: "white", borderRadius: "50%", width: "52px", height: "52px", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 4px 12px rgba(0,0,0,0.25)", border: "none", cursor: "pointer" }}
        aria-label="Chat">
        {open ? <X size={22} /> : <MessageCircle size={22} />}
      </button>

      {open && (
        <div style={{ position: "fixed", bottom: "150px", right: "20px", zIndex: 999, width: "340px", maxWidth: "calc(100vw - 48px)", backgroundColor: "white", borderRadius: "16px", boxShadow: "0 8px 30px rgba(0,0,0,0.2)", border: "1px solid #e5e7eb", display: "flex", flexDirection: "column", overflow: "hidden", height: "420px" }}>
          <div style={{ backgroundColor: "#4caf50", color: "white", padding: "12px 16px", fontWeight: "bold", display: "flex", alignItems: "center", gap: "8px" }}>
            <MessageCircle size={18} /> {t("chat_title")}
          </div>
          <div style={{ flex: 1, overflowY: "auto", padding: "12px", display: "flex", flexDirection: "column", gap: "12px", fontSize: "14px" }}>
            {messages.map((m, i) =>
              m.role === "suggestions" ? (
                <div key={i} style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                  {m.items.map((s, j) => (
                    <button key={j} onClick={() => send(s)} style={{ fontSize: "12px", backgroundColor: "#e8f5e9", color: "#2e7d32", padding: "4px 12px", borderRadius: "9999px", border: "1px solid #a5d6a7", cursor: "pointer" }}>{s}</button>
                  ))}
                </div>
              ) : (
                <div key={i} style={{ display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
                  <div style={{ maxWidth: "80%", padding: "8px 12px", borderRadius: "16px", backgroundColor: m.role === "user" ? "#4caf50" : "#f3f4f6", color: m.role === "user" ? "white" : "#1f2937", borderBottomRightRadius: m.role === "user" ? "4px" : "16px", borderBottomLeftRadius: m.role === "user" ? "16px" : "4px" }}>
                    {m.content}
                  </div>
                </div>
              )
            )}
            {loading && <div style={{ backgroundColor: "#f3f4f6", padding: "8px 12px", borderRadius: "16px", color: "#9ca3af", fontSize: "12px" }}>Typing...</div>}
            <div ref={bottomRef} />
          </div>
          <div style={{ borderTop: "1px solid #e5e7eb", padding: "12px", display: "flex", gap: "8px" }}>
            <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder={t("chat_placeholder")}
              style={{ flex: 1, border: "1px solid #d1d5db", borderRadius: "9999px", padding: "8px 16px", fontSize: "14px", outline: "none" }} />
            <button onClick={() => send()} style={{ backgroundColor: "#4caf50", color: "white", borderRadius: "50%", width: "36px", height: "36px", display: "flex", alignItems: "center", justifyContent: "center", border: "none", cursor: "pointer" }}>
              <Send size={16} />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
