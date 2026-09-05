import logging
import time
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from .config import get_settings
from .models import Message, Session
from .providers import get_provider
from .retrieval import retrieve

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM = """You are The Lenny Growth Assistant, an internal product and growth research assistant.

GROUNDING RULES:
- Use only the supplied transcript excerpts as factual knowledge.
- Do not use outside knowledge, web knowledge, or unstated assumptions as facts.
- If the excerpts do not support an answer, say so clearly.
- For supported claims, cite the source inline as [Source: title].
- Distinguish a guest's advice from your own synthesis.
- The user's previous messages provide conversational context only; they are not evidence.
- Be concise but useful. For strategic questions, give a structured answer with practical implications.
"""

def build_context(rows):
    if not rows:
        return "No relevant transcript excerpts were retrieved."
    blocks = []
    for i, row in enumerate(rows, 1):
        blocks.append(
            f"""EXCERPT {i}
Title: {row['title']}
Guest: {row.get('guest') or 'Unknown'}
Source: {row['source_path']}
Relevance: {row['relevance']:.3f}
Text:
{row['text']}
"""
        )
    return "\n---\n".join(blocks)


def answer(db: DBSession, session_id: str, user_message: str, provider_name: str | None = None):
    started = time.perf_counter()
    session = db.get(Session, session_id)
    if not session:
        raise ValueError("Session not found")

    provider = get_provider(provider_name)

    # Embed only the new user turn for retrieval; history is supplied to the model separately.
    embedding = provider.embed([user_message])[0]
    rows = retrieve(db, embedding, settings.top_k)

    history = db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
        .limit(20)
    ).scalars().all()

    messages = [
        {"role": m.role, "content": m.content}
        for m in history
        if m.role in {"user", "assistant"}
    ]
    messages.append(
        {
            "role": "user",
            "content": f"""Answer the latest question using the transcript context below.

TRANSCRIPT CONTEXT:
{build_context(rows)}

LATEST USER QUESTION:
{user_message}
""",
        }
    )

    text = provider.generate(SYSTEM, messages)
    latency = int((time.perf_counter() - started) * 1000)

    sources = [
        {
            "title": r["title"],
            "source_path": r["source_path"],
            "guest": r.get("guest"),
            "chunk_id": r["chunk_id"],
            "relevance": r["relevance"],
        }
        for r in rows
    ]
    return text, sources, provider.name, provider.model, latency
