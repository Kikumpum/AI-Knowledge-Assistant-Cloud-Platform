import json
import logging
import os
from pathlib import Path

import aiofiles
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.infrastructure.embedding_service import EmbeddingService
from app.infrastructure.models import Document, User
from app.infrastructure.repositories import DocumentRepository
from app.infrastructure.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


class DocumentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = DocumentRepository(session)
        self.settings = get_settings()

    def _validate_extension(self, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError("Only PDF and TXT files are allowed")
        return ext.lstrip(".")

    async def save_upload(self, user: User, filename: str, content: bytes) -> Document:
        if len(content) > self.settings.max_upload_bytes:
            raise ValueError(f"File exceeds {self.settings.max_upload_size_mb}MB limit")

        file_type = self._validate_extension(filename)
        upload_dir = Path(self.settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        doc = await self.repo.create(user.id, filename, file_type)

        safe_name = f"{doc.id}_{Path(filename).name}"
        file_path = upload_dir / safe_name

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        try:
            text = self._extract_text(file_path, file_type)
            chunk_count, chroma_ids = await self._index_document(
                text=text,
                filename=filename,
                user_id=user.id,
                document_id=doc.id,
            )
            await self.repo.update_processed(doc, chunk_count, chroma_ids)
        except Exception as e:
            logger.exception("Document indexing failed: %s", e)
            await self.repo.update_failed(doc)
            raise

        return doc

    def _extract_text(self, file_path: Path, file_type: str) -> str:
        if file_type == "txt":
            return file_path.read_text(encoding="utf-8", errors="ignore")
        reader = PdfReader(str(file_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)

    async def _index_document(
        self,
        text: str,
        filename: str,
        user_id: int,
        document_id: int,
    ) -> tuple[int, list[str]]:
        if not text.strip():
            raise ValueError("Document contains no extractable text")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        chunks = splitter.split_text(text)
        if not chunks:
            raise ValueError("No chunks generated from document")

        embedding_svc = EmbeddingService.get_instance()
        vector_store = VectorStoreService.get_instance()

        embeddings = embedding_svc.embed_texts(chunks)
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
        chroma_ids = vector_store.add_documents(
            texts=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            user_id=user_id,
            document_id=document_id,
        )
        return len(chunks), chroma_ids

    async def list_documents(self, user_id: int) -> list[Document]:
        return list(await self.repo.list_by_user(user_id))

    async def delete_document(self, user: User, document_id: int) -> bool:
        doc = await self.repo.get_by_id(document_id, user.id)
        if not doc:
            return False
        if doc.chroma_ids:
            ids = json.loads(doc.chroma_ids)
            VectorStoreService.get_instance().delete_by_ids(ids)
        upload_dir = Path(self.settings.upload_dir)
        for f in upload_dir.glob(f"{doc.id}_*"):
            try:
                os.remove(f)
            except OSError:
                pass
        await self.repo.delete(doc)
        return True
