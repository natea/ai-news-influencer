"""Embedding generation for RAG system."""
from typing import Optional

from openai import AsyncOpenAI
from pydantic import BaseModel

from src.core.config import get_settings
from src.database.vector_store import VectorDocument, vector_store


class EmbeddingResult(BaseModel):
    """Result of embedding generation."""
    embedding: list[float]
    tokens_used: int
    model: str


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self):
        settings = get_settings()
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.embedding_model

    async def embed_text(self, text: str) -> EmbeddingResult:
        """Generate embedding for a single text."""
        response = await self._client.embeddings.create(
            model=self._model,
            input=text
        )

        return EmbeddingResult(
            embedding=response.data[0].embedding,
            tokens_used=response.usage.total_tokens,
            model=self._model
        )

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []

        response = await self._client.embeddings.create(
            model=self._model,
            input=texts
        )

        tokens_per_text = response.usage.total_tokens // len(texts)

        return [
            EmbeddingResult(
                embedding=data.embedding,
                tokens_used=tokens_per_text,
                model=self._model
            )
            for data in response.data
        ]

    async def store_post(
        self,
        post_id: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> None:
        """Generate embedding and store post in vector store."""
        result = await self.embed_text(content)

        doc = VectorDocument(
            id=f"post:{post_id}",
            content=content,
            embedding=result.embedding,
            metadata=metadata or {}
        )

        vector_store.add_document(doc)

    async def search_similar(
        self,
        query: str,
        k: int = 5,
        doc_type: Optional[str] = None
    ) -> list[dict]:
        """Search for similar content."""
        result = await self.embed_text(query)

        search_results = vector_store.search(result.embedding, k=k)

        # Filter by document type if specified
        if doc_type:
            search_results = [
                r for r in search_results
                if r.id.startswith(f"{doc_type}:")
            ]

        return [
            {
                "id": r.id,
                "content": r.content,
                "score": r.score,
                "metadata": r.metadata
            }
            for r in search_results
        ]


# Global instance
embedding_service = EmbeddingService()
