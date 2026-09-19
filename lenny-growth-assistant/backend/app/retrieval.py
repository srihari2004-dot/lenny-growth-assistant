from sqlalchemy import select, text
from sqlalchemy.orm import Session
from .models import Chunk, Document


def retrieve(db: Session, embedding: list[float], top_k: int):
    """Semantic retrieval for the local Ollama path."""
    distance = Chunk.embedding.cosine_distance(embedding)
    rows = db.execute(
        select(Chunk, Document, distance.label("distance"))
        .join(Document, Chunk.document_id == Document.id)
        .where(Chunk.embedding.is_not(None))
        .order_by(distance)
        .limit(top_k)
    ).all()

    return [
        {
            "chunk_id": chunk.id,
            "text": chunk.text,
            "title": document.title,
            "source_path": document.source_path,
            "guest": document.guest,
            "relevance": max(0.0, min(1.0, 1.0 - float(distance))),
        }
        for chunk, document, distance in rows
    ]


def retrieve_keyword(db: Session, query: str, top_k: int):
    """Cloud-safe retrieval that requires no external embedding service.

    PostgreSQL full-text search is used for the deployed Anthropic path. This
    keeps the public service independent from a user's local Ollama instance.
    """
    sql = text(
        """
        WITH q AS (
            SELECT websearch_to_tsquery('english', :query) AS tsq
        ), ranked AS (
            SELECT
                c.id AS chunk_id,
                c.text AS chunk_text,
                d.title AS title,
                d.source_path AS source_path,
                d.guest AS guest,
                ts_rank_cd(
                    to_tsvector('english', coalesce(d.title, '') || ' ' || c.text),
                    q.tsq
                ) AS rank
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            CROSS JOIN q
            WHERE q.tsq @@ to_tsvector(
                'english', coalesce(d.title, '') || ' ' || c.text
            )
        )
        SELECT chunk_id, chunk_text, title, source_path, guest, rank
        FROM ranked
        ORDER BY rank DESC, chunk_id
        LIMIT :top_k
        """
    )

    rows = db.execute(sql, {"query": query, "top_k": top_k}).mappings().all()

    if not rows:
        # FTS can legitimately produce no terms for very short/stop-word-heavy
        # questions. Fall back to a conservative ILIKE search so the assistant
        # can still ground an answer rather than failing retrieval entirely.
        terms = [t.strip() for t in query.replace("?", " ").split() if len(t.strip()) >= 4]
        if terms:
            conditions = " OR ".join([f"c.text ILIKE :term{i}" for i in range(len(terms))])
            params = {f"term{i}": f"%{term}%" for i, term in enumerate(terms)}
            fallback = text(
                f"""
                SELECT c.id AS chunk_id, c.text AS chunk_text,
                       d.title AS title, d.source_path AS source_path,
                       d.guest AS guest
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE {conditions}
                LIMIT :top_k
                """
            )
            rows = db.execute(fallback, {**params, "top_k": top_k}).mappings().all()
            return [
                {
                    "chunk_id": r["chunk_id"],
                    "text": r["chunk_text"],
                    "title": r["title"],
                    "source_path": r["source_path"],
                    "guest": r["guest"],
                    "relevance": 0.35,
                }
                for r in rows
            ]

    max_rank = max((float(r["rank"]) for r in rows), default=1.0)
    return [
        {
            "chunk_id": r["chunk_id"],
            "text": r["chunk_text"],
            "title": r["title"],
            "source_path": r["source_path"],
            "guest": r["guest"],
            "relevance": max(0.0, min(1.0, float(r["rank"]) / max_rank if max_rank else 0.0)),
        }
        for r in rows
    ]
