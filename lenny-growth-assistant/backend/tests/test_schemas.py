import pytest
from pydantic import ValidationError
from app.schemas import ChatRequest


def test_chat_message_required():
    with pytest.raises(ValidationError):
        ChatRequest(session_id="x", message="")
