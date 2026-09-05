from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Chunk, Document


def retrieve(db: Session, embedding: list[float], top_k: int):
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
