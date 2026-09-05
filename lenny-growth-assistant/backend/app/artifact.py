import nh3
from .providers import get_provider
from .ship30 import SHIP_30_SKILL
from .models import Message
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

ARTIFACT_SYSTEM = """You generate artifacts for The Lenny Growth Assistant.

Only use the supplied conversation and transcript-grounded answer as factual input.
Never add outside facts.

For HTML:
- Return a complete HTML fragment suitable for srcdoc.
- Inline CSS is allowed.
- Do not include <script>, event-handler attributes, forms, iframes, objects, embeds, or external active content.
- Keep the document visually polished and readable.

For Markdown:
- Return clean Markdown only.
"""

ALLOWED_TAGS = {
    "article", "section", "header", "footer", "h1", "h2", "h3", "h4",
    "p", "ul", "ol", "li", "strong", "em", "blockquote", "code", "pre",
    "table", "thead", "tbody", "tr", "th", "td", "a", "hr", "br", "div",
    "span"
}
ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "*": {"class", "id"}
}


def sanitize_html(html: str) -> str:
    return nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes={"http", "https", "mailto"},
        strip_comments=True,
    )


def generate_artifact(db: DBSession, session_id: str, instruction: str, fmt: str):
    history = db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
        .limit(30)
    ).scalars().all()
    if not history:
        raise ValueError("Session has no conversation yet")

    transcript = "\n\n".join(f"{m.role.upper()}: {m.content}" for m in history)
    system = ARTIFACT_SYSTEM
    if "ship 30" in instruction.lower() or "essay" in instruction.lower():
        system += "\n\n" + SHIP_30_SKILL

    prompt = f"""Create a {fmt} artifact according to this instruction:
{instruction}

Conversation:
{transcript}
"""
    provider = get_provider()
    content = provider.generate(system, [{"role": "user", "content": prompt}], max_tokens=2200)
    if fmt == "html":
        content = sanitize_html(content)
    return content
