# Architecture

## Overview

```text
React UI
  |
  | HTTP/JSON
  v
FastAPI
  |
  +--> Session / message persistence --> PostgreSQL
  |
  +--> Retrieval --> pgvector
  |                    ^
  |                    |
  |              Ollama embeddings
  |
  +--> Agent/orchestration
          |
          +--> Ollama chat model (required local demo)
          |
          +--> Anthropic provider (optional cloud)
          |
          +--> Ship 30 skill
          |
          +--> Artifact sanitizer
```

## Database

### sessions

- id
- title
- user_metadata
- created_at

### messages

- id
- session_id
- role
- content
- created_at
- metadata_json

### documents

- id
- source_path
- title
- source_type
- guest
- content_hash

### chunks

- id
- document_id
- chunk_index
- text
- embedding vector(768)

PostgreSQL + pgvector keeps relational persistence and vector retrieval in one system.

## Ingestion

Source Markdown → metadata extraction → normalized text → overlapping chunks → Ollama embeddings → PostgreSQL.

Content hashes make re-ingestion idempotent for unchanged files.

## Retrieval

Question → Ollama embedding → cosine-distance search in pgvector → top-k chunks → source-labelled context.

The assistant does not search the public web.

## Agent routing

The application has a provider interface:

```text
LLMProvider
  ├── OllamaProvider
  └── AnthropicProvider
```

This allows the model to change through configuration/UI without changing the application workflow.

The repository also includes a Claude Agent SDK adapter. The local Ollama path remains the primary demo because the assignment explicitly requires it.

## Artifact security

1. Model generates artifact.
2. Backend sanitizes HTML with an allowlist.
3. Frontend uses `<iframe sandbox="">`.
4. No script/same-origin permissions are granted.

This blocks common active-content paths while allowing static HTML/CSS to render.

## Resilience

- DB health check
- request timeouts for Ollama
- explicit provider errors
- no silent cloud fallback
- source-empty retrieval is represented to the model
- API returns structured HTTP errors
- JSON logs contain request IDs but not prompts/secrets
