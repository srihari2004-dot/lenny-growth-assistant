from datetime import datetime
from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    title: str = Field(default="New chat", max_length=200)


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: datetime


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1, max_length=12000)
    provider: str | None = None


class Source(BaseModel):
    title: str
    source_path: str
    guest: str | None = None
    chunk_id: int
    relevance: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    provider: str
    model: str
    latency_ms: int


class ArtifactRequest(BaseModel):
    session_id: str
    instruction: str = Field(min_length=1, max_length=5000)
    format: str = Field(default="html", pattern="^(html|markdown)$")


class ArtifactResponse(BaseModel):
    format: str
    content: str
    title: str
