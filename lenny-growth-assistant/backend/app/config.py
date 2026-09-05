from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://lenny:lenny@db:5432/lenny"

    llm_provider: str = "ollama"
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_chat_model: str = "llama3.2:3b"
    ollama_embed_model: str = "embeddinggemma"

    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-6"

    top_k: int = 6
    chunk_size: int = 1400
    chunk_overlap: int = 220
    cors_origins: str = "http://localhost:5173"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
