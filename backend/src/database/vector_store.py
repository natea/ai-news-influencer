"""Vector store using sqlite-vss for RAG functionality."""
import json
import sqlite3
from pathlib import Path
from typing import Optional

import numpy as np
from pydantic import BaseModel

from src.core.config import get_settings


class VectorDocument(BaseModel):
    """A document stored in the vector store."""
    id: str
    content: str
    embedding: list[float]
    metadata: dict = {}


class SearchResult(BaseModel):
    """Result from a vector search."""
    id: str
    content: str
    score: float
    metadata: dict = {}


class VectorStore:
    """SQLite-based vector store with VSS extension."""

    def __init__(self, db_path: str = "./data/vectors.db"):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._dimension = 1536  # OpenAI text-embedding-3-small dimension

    def connect(self) -> None:
        """Connect to the database and initialize VSS."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self._conn = sqlite3.connect(self.db_path)
        self._conn.enable_load_extension(True)

        try:
            # Try to load sqlite-vss extension
            self._conn.load_extension("vss0")
            self._conn.load_extension("vector0")
        except Exception:
            # Fallback: use pure Python similarity search
            print("Warning: sqlite-vss not available, using fallback similarity search")

        self._conn.enable_load_extension(False)
        self._initialize_tables()

    def _initialize_tables(self) -> None:
        """Create necessary tables."""
        cursor = self._conn.cursor()

        # Main documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                embedding BLOB NOT NULL,
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Try to create VSS virtual table
        try:
            cursor.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS vss_documents USING vss0(
                    embedding({self._dimension})
                )
            """)
        except Exception:
            # VSS not available, will use fallback
            pass

        self._conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def add_document(self, doc: VectorDocument) -> None:
        """Add a document to the vector store."""
        cursor = self._conn.cursor()

        # Store in main table
        embedding_blob = np.array(doc.embedding, dtype=np.float32).tobytes()
        cursor.execute(
            "INSERT OR REPLACE INTO documents (id, content, embedding, metadata) VALUES (?, ?, ?, ?)",
            (doc.id, doc.content, embedding_blob, json.dumps(doc.metadata))
        )

        # Try to add to VSS index
        try:
            cursor.execute(
                "INSERT INTO vss_documents (rowid, embedding) VALUES (?, ?)",
                (hash(doc.id) % (2**31), json.dumps(doc.embedding))
            )
        except Exception:
            pass

        self._conn.commit()

    def search(
        self,
        query_embedding: list[float],
        k: int = 5,
        threshold: float = 0.0
    ) -> list[SearchResult]:
        """Search for similar documents."""
        cursor = self._conn.cursor()

        # Try VSS search first
        try:
            cursor.execute(
                """
                SELECT rowid, distance
                FROM vss_documents
                WHERE vss_search(embedding, ?)
                LIMIT ?
                """,
                (json.dumps(query_embedding), k)
            )
            vss_results = cursor.fetchall()

            results = []
            for rowid, distance in vss_results:
                cursor.execute(
                    "SELECT id, content, metadata FROM documents WHERE hash(id) % 2147483648 = ?",
                    (rowid,)
                )
                row = cursor.fetchone()
                if row:
                    score = 1.0 - distance  # Convert distance to similarity
                    if score >= threshold:
                        results.append(SearchResult(
                            id=row[0],
                            content=row[1],
                            score=score,
                            metadata=json.loads(row[2])
                        ))
            return results

        except Exception:
            # Fallback: brute force similarity search
            return self._fallback_search(query_embedding, k, threshold)

    def _fallback_search(
        self,
        query_embedding: list[float],
        k: int,
        threshold: float
    ) -> list[SearchResult]:
        """Fallback similarity search using numpy."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT id, content, embedding, metadata FROM documents")
        rows = cursor.fetchall()

        if not rows:
            return []

        query_vec = np.array(query_embedding, dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)

        results = []
        for row in rows:
            doc_vec = np.frombuffer(row[2], dtype=np.float32)
            doc_norm = np.linalg.norm(doc_vec)

            if query_norm > 0 and doc_norm > 0:
                similarity = np.dot(query_vec, doc_vec) / (query_norm * doc_norm)
            else:
                similarity = 0.0

            if similarity >= threshold:
                results.append(SearchResult(
                    id=row[0],
                    content=row[1],
                    score=float(similarity),
                    metadata=json.loads(row[3])
                ))

        # Sort by score and return top k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:k]

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the store."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    def get_document(self, doc_id: str) -> Optional[VectorDocument]:
        """Get a document by ID."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, content, embedding, metadata FROM documents WHERE id = ?",
            (doc_id,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        embedding = np.frombuffer(row[2], dtype=np.float32).tolist()
        return VectorDocument(
            id=row[0],
            content=row[1],
            embedding=embedding,
            metadata=json.loads(row[3])
        )


# Global instance
vector_store = VectorStore()
