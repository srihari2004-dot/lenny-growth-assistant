import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { chat, createArtifact, createSession, getMessages, Message, Source } from "./api";

type ChatItem = Message & { sources?: Source[] };

export default function App() {
  const [sessionId, setSessionId] = useState("");
  const [messages, setMessages] = useState<ChatItem[]>([]);
  const [input, setInput] = useState("");
  const [provider, setProvider] = useState("ollama");
  const [busy, setBusy] = useState(false);
  const [artifact, setArtifact] = useState<{format: string, content: string} | null>(null);
  const [artifactBusy, setArtifactBusy] = useState(false);
  const [error, setError] = useState("");

  async function newChat() {
    setError("");
    const s = await createSession();
    setSessionId(s.id);
    setMessages([]);
    setArtifact(null);
  }

  useEffect(() => { newChat().catch(e => setError(String(e))); }, []);

  async function send() {
    if (!input.trim() || busy || !sessionId) return;
    const text = input.trim();
    setInput("");
    setError("");
    setMessages(prev => [...prev, {role: "user", content: text, created_at: new Date().toISOString()}]);
    setBusy(true);
    try {
      const result = await chat(sessionId, text, provider);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: result.answer,
        created_at: new Date().toISOString(),
        sources: result.sources
      }]);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function makeArtifact(format: "html" | "markdown") {
    if (!sessionId) return;
    setArtifactBusy(true);
    setError("");
    try {
      const result = await createArtifact(
        sessionId,
        format === "html"
          ? "Create a polished one-page product strategy artifact summarizing the key advice in this conversation."
          : "Create a concise Ship 30 for 30 style essay from the grounded ideas in this conversation.",
        format
      );
      setArtifact({format: result.format, content: result.content});
    } catch (e) {
      setError(String(e));
    } finally {
      setArtifactBusy(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <div className="eyebrow">LENNY'S KNOWLEDGE BASE</div>
          <h1>The Lenny Growth Assistant</h1>
        </div>
        <div className="controls">
          <label>Model
            <select value={provider} onChange={e => setProvider(e.target.value)}>
              <option value="ollama">Ollama · local demo</option>
              <option value="anthropic">Anthropic · cloud</option>
            </select>
          </label>
          <button onClick={newChat}>+ New chat</button>
        </div>
      </header>

      <main className="workspace">
        <section className="chat-panel">
          <div className="status">
            <span className="dot"></span>
            Grounded mode · answers cite transcript sources
          </div>

          <div className="messages">
            {messages.length === 0 && (
              <div className="empty">
                <h2>Ask a product or growth question.</h2>
                <p>Try: “What patterns do Lenny’s guests recommend for improving activation?”</p>
              </div>
            )}
            {messages.map((m, i) => (
              <article key={i} className={`message ${m.role}`}>
                <div className="role">{m.role === "user" ? "YOU" : "LENNY ASSISTANT"}</div>
                <ReactMarkdown>{m.content}</ReactMarkdown>
                {m.sources && m.sources.length > 0 && (
                  <div className="sources">
                    <div className="source-label">SOURCES</div>
                    {m.sources.slice(0, 4).map((s, j) => (
                      <div className="source" key={j}>
                        <strong>{s.title}</strong>
                        {s.guest && <span> · {s.guest}</span>}
                        <small> relevance {(s.relevance * 100).toFixed(0)}%</small>
                      </div>
                    ))}
                  </div>
                )}
              </article>
            ))}
            {busy && <div className="thinking">Searching transcripts and composing a grounded answer…</div>}
          </div>

          {error && <div className="error">{error}</div>}

          <div className="composer">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }}}
              placeholder="Ask about product, growth, activation, retention, pricing…"
              rows={3}
            />
            <button className="send" disabled={busy || !input.trim()} onClick={send}>Send</button>
          </div>
        </section>

        <aside className="artifact-panel">
          <div className="artifact-head">
            <div>
              <div className="eyebrow">ARTIFACT VIEWER</div>
              <h2>Rendered output</h2>
            </div>
            <div className="artifact-actions">
              <button disabled={artifactBusy} onClick={() => makeArtifact("html")}>HTML</button>
              <button disabled={artifactBusy} onClick={() => makeArtifact("markdown")}>Markdown</button>
            </div>
          </div>

          {!artifact && (
            <div className="artifact-empty">
              <p>Generate an artifact from the current conversation.</p>
              <p className="muted">HTML is sanitized server-side and rendered in a sandboxed frame.</p>
            </div>
          )}

          {artifact?.format === "html" && (
            <iframe
              className="artifact-frame"
              sandbox=""
              title="Generated artifact"
              srcDoc={artifact.content}
            />
          )}

          {artifact?.format === "markdown" && (
            <div className="artifact-markdown">
              <ReactMarkdown>{artifact.content}</ReactMarkdown>
            </div>
          )}
        </aside>
      </main>
    </div>
  );
}
