# The Lenny Growth Assistant

A full-stack, source-grounded conversational assistant for Lenny's Podcast/Newsletter transcripts.

## What this submission demonstrates

- FastAPI backend with typed request/response contracts
- PostgreSQL + pgvector persistence
- RAG over transcript chunks with source citations
- Local Ollama model for the required demo
- Optional Anthropic Claude cloud provider
- Provider/model toggle without changing application code
- Independent chat sessions and persisted messages
- Ship 30 for 30 writing skill
- Markdown/HTML artifact generation
- Sandboxed artifact viewer
- Structured logging, health checks, graceful failures
- Automated backend tests
- Docker Compose one-command startup

The public Lenny starter dataset contains 50 podcast transcripts and 10 newsletter posts. This project intentionally does not commit the dataset; use the fetch script to download the public starter pack locally.

## Quick start

### Prerequisites

- Docker Desktop
- 8 GB+ RAM recommended for Ollama
- An Ollama model that can run comfortably on your machine

### 1. Start the stack

```bash
cp .env.example .env
docker compose up --build
```

The app is available at:

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health

### 2. Prepare Ollama

On the host machine:

```bash
ollama pull llama3.2:3b
ollama pull embeddinggemma
```

The application connects to Ollama at `http://host.docker.internal:11434`.

If your machine is resource constrained, use another small chat model and change `OLLAMA_CHAT_MODEL` in `.env`.

### 3. Fetch the public starter transcripts

```bash
python scripts/fetch_transcripts.py
```

This clones the public starter repository into `data/lenny-source`.

### 4. Ingest the transcripts

```bash
docker compose exec api python -m app.ingest
```

The ingestion pipeline:

1. discovers Markdown transcript files
2. extracts title/guest/source metadata
3. chunks content with overlap
4. creates Ollama embeddings
5. stores documents/chunks/embeddings in PostgreSQL
6. skips unchanged chunks on repeated runs

### 5. Open the application

Go to http://localhost:5173 and ask a product/growth question.

The UI displays the selected provider/model and source citations for grounded answers.

## Optional Claude setup

Set:

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key
ANTHROPIC_MODEL=claude-sonnet-4-6
```

The cloud provider uses the official Anthropic Python SDK. The project keeps the provider interface identical to the Ollama implementation.

For the assignment's agent requirement, the repository also includes `claude-agent-sdk` and a small agent integration example under `backend/app/agent_sdk.py`. The production chat path uses the provider abstraction because Ollama must remain a first-class local demo path.

## Project structure

```text
backend/
  app/
    agent.py             # grounded orchestration
    agent_sdk.py         # Claude Agent SDK integration example
    artifact.py          # artifact generation
    config.py
    db.py
    main.py
    models.py
    providers.py         # Ollama / Anthropic provider abstraction
    retrieval.py         # pgvector retrieval
    schemas.py
    ship30.py            # dedicated writing skill
    logging_config.py
  tests/

frontend/
  src/
    App.tsx
    api.ts
    main.tsx
    styles.css

scripts/
  fetch_transcripts.py

docs/
  agent-transcripts/
    README.md
  manual-test-plan.md

PRD.md
design.md
architecture.md
docker-compose.yml
```

## API

### `POST /api/sessions`

Creates an independent conversation session.

### `GET /api/sessions`

Lists recent sessions.

### `GET /api/sessions/{session_id}/messages`

Returns the persisted conversation.

### `POST /api/chat`

Request:

```json
{
  "session_id": "uuid",
  "message": "How should I think about activation?",
  "provider": "ollama"
}
```

Response includes:

- answer
- sources
- provider
- model
- latency metadata

### `POST /api/artifacts`

Generates a Markdown or HTML/CSS artifact from the current conversation.

### `GET /health`

Returns service/database/Ollama readiness.

## Grounding policy

The assistant is deliberately conservative:

- It may only use retrieved transcript context for substantive claims.
- It must cite the transcript title/source for supported claims.
- It should say that the available material does not support an answer rather than inventing a fact.
- Conversation history is used to resolve follow-up references, but history itself is not treated as authoritative knowledge.
- Retrieval failure is surfaced as a useful error instead of silently producing an uncited answer.

## Security

Generated HTML is untrusted.

The backend sanitizes generated HTML with an allowlist. The frontend renders it inside a sandboxed iframe without `allow-scripts` or `allow-same-origin`. Scripts, event-handler attributes, embedded frames, forms, objects, and similar active content are removed/blocked.

This is intentionally stricter than a general-purpose website renderer because the assessment asks for a safe artifact viewer.

## Testing

```bash
docker compose exec api pytest -q
```

The tests cover:

- health behavior
- session creation
- grounding behavior
- provider routing
- artifact sanitization

## Troubleshooting

### Ollama unavailable

Make sure Ollama is running on the host:

```bash
ollama list
```

Then verify:

```bash
curl http://localhost:11434/api/tags
```

On Linux, `host.docker.internal` may require Docker's host-gateway mapping; the included Compose file provides it.

### No retrieval results

Run ingestion again:

```bash
docker compose exec api python -m app.ingest
```

Check that the embedding model exists:

```bash
ollama list
```

### Database connection errors

```bash
docker compose ps
docker compose logs db
```

The API retries database startup and exposes `/health` for diagnosis.

## Scope decisions

Included:
- transcript ingestion
- grounded chat
- session persistence
- provider switching
- artifact generation/viewing
- writing skill
- tests and operational documentation

Excluded:
- production authentication/SSO
- multi-tenant authorization
- streaming tokens
- background job queues
- production cloud deployment

Those are intentionally out of scope for a take-home MVP so that grounding, deployment quality, and evaluator usability remain the focus.
