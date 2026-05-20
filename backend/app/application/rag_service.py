import logging
from typing import Any, Optional

from app.core.config import get_settings
from app.infrastructure.embedding_service import EmbeddingService
from app.infrastructure.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful AI assistant. Answer based on the provided context.
If the context does not contain relevant information, say so honestly and answer from general knowledge briefly.
Cite sources when using context."""


class RAGService:
    async def generate_response(
        self,
        query: str,
        user_id: int,
        history: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        settings = get_settings()
        embedding_svc = EmbeddingService.get_instance()
        vector_store = VectorStoreService.get_instance()

        query_embedding = embedding_svc.embed_query(query)
        retrieved = vector_store.search(
            query_embedding=query_embedding,
            user_id=user_id,
            top_k=settings.top_k_results,
        )

        context_block = self._build_context(retrieved)
        sources = [
            {
                "content": r["content"][:200] + ("..." if len(r["content"]) > 200 else ""),
                "source": r["metadata"].get("source", "unknown"),
                "score": round(r["score"], 4),
            }
            for r in retrieved
        ]

        if settings.use_openai and settings.openai_api_key:
            answer = await self._openai_generate(query, context_block, history)
        else:
            answer = self._local_generate(query, context_block, retrieved)

        return {"answer": answer, "sources": sources}

    def _build_context(self, retrieved: list[dict[str, Any]]) -> str:
        if not retrieved:
            return "No relevant documents found in knowledge base."
        parts = []
        for i, item in enumerate(retrieved, 1):
            source = item["metadata"].get("source", "document")
            parts.append(f"[{i}] Source: {source}\n{item['content']}")
        return "\n\n".join(parts)

    def _local_generate(
        self,
        query: str,
        context: str,
        retrieved: list[dict[str, Any]],
    ) -> str:
        if not retrieved:
            return (
                f"I couldn't find relevant information in your knowledge base for: "
                f'"{query}"\n\n'
                "Please upload PDF or TXT documents to build your knowledge base, "
                "then ask again."
            )

        top = retrieved[0]
        source = top["metadata"].get("source", "your documents")
        snippet = top["content"][:800]

        response = (
            f"Based on your knowledge base (source: **{source}**), here is what I found:\n\n"
            f"{snippet}"
        )
        if len(retrieved) > 1:
            other_sources = {r["metadata"].get("source", "?") for r in retrieved[1:]}
            response += f"\n\n_Additional references: {', '.join(other_sources)}_"
        response += f"\n\n---\n*Your question:* {query}"
        return response

    async def _openai_generate(
        self,
        query: str,
        context: str,
        history: Optional[list[dict[str, str]]],
    ) -> str:
        import httpx

        settings = get_settings()
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append(
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}",
            }
        )

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.llm_model,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 1024,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
