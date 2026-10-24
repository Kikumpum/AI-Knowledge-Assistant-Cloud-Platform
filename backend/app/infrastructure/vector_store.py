import logging
import uuid
from typing import Any, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    """ChromaDB client wrapper for embedding storage and similarity search."""

    _instance: Optional["VectorStoreService"] = None

    def __init__(self) -> None:
        settings = get_settings()
        self._collection_name = settings.chroma_collection
        client_settings = ChromaSettings(anonymized_telemetry=False)
        if settings.chroma_mode == "local":
            self._client = chromadb.PersistentClient(
                path=settings.chroma_path,
                settings=client_settings,
            )
        else:
            self._client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
                settings=client_settings,
            )
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    @classmethod
    def get_instance(cls) -> "VectorStoreService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add_documents(
        self,
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
        user_id: int,
        document_id: int,
    ) -> list[str]:
        ids = [f"doc_{document_id}_{uuid.uuid4().hex[:12]}" for _ in texts]
        enriched_meta = [
            {**m, "user_id": str(user_id), "document_id": str(document_id)} for m in metadatas
        ]
        self._collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=enriched_meta,
        )
        return ids

    def search(
        self,
        query_embedding: list[float],
        user_id: int,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        settings = get_settings()
        k = top_k or settings.top_k_results
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where={"user_id": str(user_id)},
            include=["documents", "metadatas", "distances"],
        )
        items: list[dict[str, Any]] = []
        if not results["documents"] or not results["documents"][0]:
            return items
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            distance = results["distances"][0][i] if results["distances"] else 0.0
            items.append(
                {
                    "content": doc,
                    "metadata": meta,
                    "score": 1.0 - distance,
                }
            )
        return items

    def delete_by_ids(self, ids: list[str]) -> None:
        if ids:
            self._collection.delete(ids=ids)

    def health_check(self) -> bool:
        try:
            self._client.heartbeat()
            return True
        except Exception as e:
            logger.warning("ChromaDB health check failed: %s", e)
            return False
