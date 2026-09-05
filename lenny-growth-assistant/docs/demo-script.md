# 2–3 minute demo script

## 0:00–0:20 — Problem

“Product and growth teams have a valuable archive in Lenny’s transcripts, but searching it manually is slow. I built an assistant that answers from that archive and shows its sources.”

## 0:20–1:00 — Grounded chat

Show the Ollama provider selected.

Ask:
“What are some approaches to improving activation?”

Point to the answer and source cards.

Ask a follow-up:
“What would that imply for an early-stage product?”

Explain that the session preserves context while retrieval remains source-driven.

## 1:00–1:30 — Artifact

Click HTML.

Show the artifact rendered beside the chat.

Click Markdown.

Explain that generated HTML is sanitized and rendered inside a sandboxed iframe.

## 1:30–2:00 — Architecture

Show the repository.

Point out:
- FastAPI
- PostgreSQL + pgvector
- Ollama
- provider abstraction
- Ship 30 skill
- tests

## 2:00–2:30 — Trade-off

“My key trade-off was prioritizing grounding and local reproducibility over broad agent autonomy. I use a small, bounded retrieval context and conservative prompting. For production I would add auth, streaming, evaluation datasets, and stronger observability.”
