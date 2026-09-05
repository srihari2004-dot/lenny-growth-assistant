from abc import ABC, abstractmethod
import httpx
from anthropic import Anthropic
from .config import get_settings

settings = get_settings()


class LLMProvider(ABC):
    name: str
    model: str

    @abstractmethod
    def generate(self, system: str, messages: list[dict[str, str]], max_tokens: int = 1200) -> str:
        raise NotImplementedError

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self):
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_chat_model
        self.embed_model = settings.ollama_embed_model

    def generate(self, system, messages, max_tokens=1200):
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, *messages],
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": max_tokens},
        }
        with httpx.Client(timeout=180) as client:
            r = client.post(f"{self.base_url}/api/chat", json=payload)
            r.raise_for_status()
            return r.json()["message"]["content"]

    def embed(self, texts):
        with httpx.Client(timeout=180) as client:
            r = client.post(
                f"{self.base_url}/api/embed",
                json={"model": self.embed_model, "input": texts},
            )
            r.raise_for_status()
            return r.json()["embeddings"]


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self):
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required for the Anthropic provider")
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    def generate(self, system, messages, max_tokens=1200):
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=0.1,
            system=system,
            messages=messages,
        )
        return "".join(block.text for block in response.content if getattr(block, "type", None) == "text")

    def embed(self, texts):
        # The chat provider does not provide embeddings in this MVP.
        # Keep ingestion on Ollama so the local demo remains self-contained.
        raise RuntimeError("Anthropic embedding is not configured; use Ollama for ingestion/retrieval embeddings")


def get_provider(name: str | None = None) -> LLMProvider:
    selected = (name or settings.llm_provider).lower()
    if selected == "ollama":
        return OllamaProvider()
    if selected == "anthropic":
        return AnthropicProvider()
    raise ValueError(f"Unsupported provider: {selected}")
