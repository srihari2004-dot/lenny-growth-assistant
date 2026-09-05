const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export type Source = {
  title: string;
  source_path: string;
  guest?: string | null;
  chunk_id: number;
  relevance: number;
};

export type Message = {
  role: string;
  content: string;
  created_at: string;
};

export async function createSession(title = "New chat") {
  const r = await fetch(`${API}/api/sessions`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({title}),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function getMessages(id: string): Promise<Message[]> {
  const r = await fetch(`${API}/api/sessions/${id}/messages`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function chat(session_id: string, message: string, provider: string) {
  const r = await fetch(`${API}/api/chat`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({session_id, message, provider}),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function createArtifact(session_id: string, instruction: string, format: "html" | "markdown") {
  const r = await fetch(`${API}/api/artifacts`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({session_id, instruction, format}),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
