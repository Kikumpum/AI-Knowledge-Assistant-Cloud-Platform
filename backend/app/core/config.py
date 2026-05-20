from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Chatbot Cloud"
    app_env: str = "development"
    debug: bool = False
    secret_key: str = "dev-secret-change-in-production"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    database_url: str = "postgresql+asyncpg://chatbot:chatbot@localhost:5432/chatbot_db"

    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection: str = "knowledge_base"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k_results: int = 5

    openai_api_key: str = ""
    llm_model: str = "gpt-3.5-turbo"
    use_openai: bool = False

    cors_origins: str = "http://localhost,http://localhost:3000"

    max_upload_size_mb: int = 10
    upload_dir: str = "./uploads"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str | List[str]) -> str:
        if isinstance(v, list):
            return ",".join(v)
        return v

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def chroma_url(self) -> str:
        return f"http://{self.chroma_host}:{self.chroma_port}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
