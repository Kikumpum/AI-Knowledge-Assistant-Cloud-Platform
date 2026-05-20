import logging
from functools import lru_cache
from typing import Optional

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Sentence Transformers embedding provider (singleton)."""

    _instance: Optional["EmbeddingService"] = None

    def __init__(self) -> None:
        settings = get_settings()
        logger.info("Loading embedding model: %s", settings.embedding_model)
        self._model = SentenceTransformer(settings.embedding_model)

    @classmethod
    def get_instance(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, show_progress_bar=False)
        return vectors.tolist()

    def embed_query(self, query: str) -> list[float]:
        vector = self._model.encode([query], show_progress_bar=False)
        return vector[0].tolist()


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService.get_instance()
