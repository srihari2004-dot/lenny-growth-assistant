import logging
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text

from .artifact import generate_artifact
from .agent import answer
from .config import get_settings
from .db import SessionLocal, init_db
from .logging_config import configure_logging, request_id
from .models import Message, Session
from .schemas import (
    ArtifactRequest, ArtifactResponse, ChatRequest, ChatResponse,
    MessageOut, SessionCreate, SessionOut,
)

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title="The Lenny Growth Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    db_ok = False
    with SessionLocal() as db:
        try:
            db.execute(text("SELECT 1"))
            db_ok = True
        except Exception:
            db_ok = False
    return {"status": "ok" if db_ok else "degraded", "database": db_ok}


@app.post("/api/sessions", response_model=SessionOut)
def create_session(payload: SessionCreate):
    with SessionLocal() as db:
        item = Session(title=payload.title)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item


@app.get("/api/sessions", response_model=list[SessionOut])
def list_sessions():
    with SessionLocal() as db:
        return db.execute(
            select(Session).order_by(Session.created_at.desc()).limit(50)
        ).scalars().all()


@app.get("/api/sessions/{session_id}/messages", response_model=list[MessageOut])
def get_messages(session_id: str):
    with SessionLocal() as db:
        if not db.get(Session, session_id):
            raise HTTPException(404, "Session not found")
        return db.execute(
            select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
        ).scalars().all()


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    rid = request_id()
    started = time.perf_counter()
    with SessionLocal() as db:
        if not db.get(Session, payload.session_id):
            raise HTTPException(404, "Session not found")

        user = Message(session_id=payload.session_id, role="user", content=payload.message)
        db.add(user)
        db.flush()

        try:
            answer_text, sources, provider, model, latency = answer(
                db, payload.session_id, payload.message, payload.provider
            )
        except Exception as exc:
            db.rollback()
            logger.exception("chat_failed", extra={"request_id": rid})
            raise HTTPException(503, f"Assistant unavailable: {exc}") from exc

        db.add(
            Message(
                session_id=payload.session_id,
                role="assistant",
                content=answer_text,
                metadata_json={"sources": sources, "provider": provider, "model": model},
            )
        )
        db.commit()

        logger.info(
            "chat_completed",
            extra={"request_id": rid, "latency_ms": int((time.perf_counter() - started) * 1000)},
        )
        return ChatResponse(
            answer=answer_text,
            sources=sources,
            provider=provider,
            model=model,
            latency_ms=latency,
        )


@app.post("/api/artifacts", response_model=ArtifactResponse)
def artifacts(payload: ArtifactRequest):
    with SessionLocal() as db:
        if not db.get(Session, payload.session_id):
            raise HTTPException(404, "Session not found")
        try:
            content = generate_artifact(db, payload.session_id, payload.instruction, payload.format)
        except Exception as exc:
            logger.exception("artifact_failed")
            raise HTTPException(503, f"Artifact generation unavailable: {exc}") from exc
        return ArtifactResponse(format=payload.format, content=content, title="Lenny Growth Artifact")
