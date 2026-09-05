import hashlib
import re
from pathlib import Path

from sqlalchemy import select
from .config import get_settings
from .db import SessionLocal, init_db
from .models import Document, Chunk
from .providers import OllamaProvider

settings = get_settings()
DATA_ROOT = Path("/app/data/lenny-source")
if not DATA_ROOT.exists():
    DATA_ROOT = Path("data/lenny-source")


def clean_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_metadata(path: Path, text: str):
    title = path.stem.replace("-", " ").replace("_", " ").strip()
    guest = None
    for line in text.splitlines()[:30]:
        if line.lower().startswith("# "):
            title = line[2:].strip()
            break
        m = re.search(r"(?:guest|with)\s*:\s*(.+)", line, flags=re.I)
        if m:
            guest = m.group(1).strip()
    return title, guest


def chunks(text: str):
    size, overlap = settings.chunk_size, settings.chunk_overlap
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        piece = text[start:end].strip()
        if piece:
            yield piece
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)


def ingest():
    init_db()
    provider = OllamaProvider()
    files = sorted(DATA_ROOT.rglob("*.md"))
    if not files:
        raise SystemExit(f"No Markdown files found under {DATA_ROOT}. Run scripts/fetch_transcripts.py first.")

    with SessionLocal() as db:
        for path in files:
            raw = path.read_text(encoding="utf-8", errors="ignore")
            text = clean_markdown(raw)
            digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            existing = db.execute(select(Document).where(Document.source_path == str(path))).scalar_one_or_none()
            if existing and existing.content_hash == digest:
                continue
            if existing:
                db.delete(existing)
                db.flush()

            title, guest = parse_metadata(path, raw)
            doc = Document(
                source_path=str(path),
                title=title,
                guest=guest,
                source_type="podcast" if "podcast" in str(path).lower() else "newsletter",
                content_hash=digest,
            )
            db.add(doc)
            db.flush()

            pieces = list(chunks(text))
            vectors = provider.embed(pieces)
            for idx, (piece, vector) in enumerate(zip(pieces, vectors)):
                db.add(Chunk(document_id=doc.id, chunk_index=idx, text=piece, embedding=vector))
            db.commit()
            print(f"Ingested {title}: {len(pieces)} chunks")


if __name__ == "__main__":
    ingest()
