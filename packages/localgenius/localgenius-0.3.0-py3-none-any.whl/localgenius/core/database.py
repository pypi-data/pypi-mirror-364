"""Database management for LocalGenius using SQLite and FAISS for vector operations."""

import json
import pickle
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import aiosqlite
import numpy as np
import faiss
from pydantic import BaseModel


class Document(BaseModel):
    """Represents a document in the database."""
    id: Optional[int] = None
    source_path: str
    content: str
    chunk_index: int
    metadata: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
    embedding_id: Optional[int] = None


class Database:
    """Manages SQLite database and FAISS index for vector storage."""
    
    def __init__(self, db_path: Path, vector_dimension: int = 1536):
        self.db_path = db_path
        self.vector_dimension = vector_dimension
        self.faiss_index_path = db_path.parent / "faiss.index"
        self.faiss_index: Optional[faiss.IndexFlatL2] = None
        self._connection: Optional[aiosqlite.Connection] = None
        
    async def initialize(self) -> None:
        """Initialize database and create tables."""
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize FAISS index
        if self.faiss_index_path.exists():
            self.faiss_index = faiss.read_index(str(self.faiss_index_path))
        else:
            self.faiss_index = faiss.IndexFlatL2(self.vector_dimension)
            
        # Create database connection and tables
        self._connection = await aiosqlite.connect(str(self.db_path))
        await self._create_tables()
        
    async def _create_tables(self) -> None:
        """Create database tables."""
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_path TEXT NOT NULL,
                content TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                embedding_id INTEGER
            )
        """)
        
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                last_indexed TIMESTAMP,
                document_count INTEGER DEFAULT 0
            )
        """)
        
        await self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_path ON documents(source_path)
        """)
        
        await self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_embedding_id ON documents(embedding_id)
        """)
        
        await self._connection.commit()
        
    async def close(self) -> None:
        """Close database connection and save FAISS index."""
        if self._connection:
            await self._connection.close()
            
        if self.faiss_index and self.faiss_index.ntotal > 0:
            faiss.write_index(self.faiss_index, str(self.faiss_index_path))
            
    async def add_document(self, document: Document, embedding: Optional[np.ndarray] = None) -> int:
        """Add a document to the database."""
        cursor = await self._connection.execute(
            """
            INSERT INTO documents (source_path, content, chunk_index, metadata)
            VALUES (?, ?, ?, ?)
            """,
            (
                document.source_path,
                document.content,
                document.chunk_index,
                json.dumps(document.metadata),
            )
        )
        
        document_id = cursor.lastrowid
        
        # Add embedding to FAISS if provided
        if embedding is not None:
            embedding_id = self.faiss_index.ntotal
            self.faiss_index.add(embedding.reshape(1, -1))
            
            await self._connection.execute(
                "UPDATE documents SET embedding_id = ? WHERE id = ?",
                (embedding_id, document_id)
            )
            
        await self._connection.commit()
        return document_id
        
    async def get_document(self, document_id: int) -> Optional[Document]:
        """Get a document by ID."""
        cursor = await self._connection.execute(
            "SELECT * FROM documents WHERE id = ?", (document_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            return Document(
                id=row[0],
                source_path=row[1],
                content=row[2],
                chunk_index=row[3],
                metadata=json.loads(row[4]) if row[4] else {},
                created_at=row[5],
                embedding_id=row[6],
            )
        return None
        
    async def search_similar(self, query_embedding: np.ndarray, k: int = 10, threshold: float = 0.7) -> List[Tuple[Document, float]]:
        """Search for similar documents using FAISS."""
        if self.faiss_index.ntotal == 0:
            return []
            
        # Search in FAISS with more results to account for duplicates
        search_k = min(k * 3, self.faiss_index.ntotal)  # Search 3x more to find diverse results
        distances, indices = self.faiss_index.search(query_embedding.reshape(1, -1), search_k)
        
        results = []
        seen_chunks = set()  # Track (source_path, chunk_index) to avoid duplicates
        
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # FAISS returns -1 for empty results
                continue
                
            # Convert L2 distance to similarity score (0-1)
            similarity = 1 / (1 + distance)
            
            if similarity < threshold:
                continue
                
            # Get document from database
            cursor = await self._connection.execute(
                "SELECT * FROM documents WHERE embedding_id = ?", (int(idx),)
            )
            row = await cursor.fetchone()
            
            if row:
                # Create unique identifier for this chunk
                chunk_id = (row[1], row[3])  # (source_path, chunk_index)
                
                # Skip if we've already seen this exact chunk
                if chunk_id in seen_chunks:
                    continue
                    
                seen_chunks.add(chunk_id)
                
                document = Document(
                    id=row[0],
                    source_path=row[1],
                    content=row[2],
                    chunk_index=row[3],
                    metadata=json.loads(row[4]) if row[4] else {},
                    created_at=row[5],
                    embedding_id=row[6],
                )
                results.append((document, similarity))
                
                # Stop when we have enough unique results
                if len(results) >= k:
                    break
                
        return results
        
    async def delete_documents_by_source(self, source_path: str) -> None:
        """Delete all documents from a specific source."""
        # Get embedding IDs to remove from FAISS
        cursor = await self._connection.execute(
            "SELECT embedding_id FROM documents WHERE source_path = ? AND embedding_id IS NOT NULL",
            (source_path,)
        )
        embedding_ids = [row[0] for row in await cursor.fetchall()]
        
        # Delete from database
        await self._connection.execute(
            "DELETE FROM documents WHERE source_path = ?", (source_path,)
        )
        await self._connection.commit()
        
        # Note: FAISS doesn't support deletion, so we'd need to rebuild the index
        # This is a limitation we'll need to handle in production
        
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        cursor = await self._connection.execute(
            "SELECT COUNT(*) FROM documents"
        )
        total_documents = (await cursor.fetchone())[0]
        
        cursor = await self._connection.execute(
            "SELECT source_path, COUNT(*) FROM documents GROUP BY source_path"
        )
        sources = {row[0]: row[1] for row in await cursor.fetchall()}
        
        return {
            "total_documents": total_documents,
            "total_embeddings": self.faiss_index.ntotal if self.faiss_index else 0,
            "sources": sources,
            "vector_dimension": self.vector_dimension,
        }
        
    async def update_data_source_stats(self, path: str, name: str) -> None:
        """Update data source statistics."""
        cursor = await self._connection.execute(
            "SELECT COUNT(*) FROM documents WHERE source_path = ?", (path,)
        )
        doc_count = (await cursor.fetchone())[0]
        
        await self._connection.execute(
            """
            INSERT OR REPLACE INTO data_sources (path, name, last_indexed, document_count)
            VALUES (?, ?, CURRENT_TIMESTAMP, ?)
            """,
            (path, name, doc_count)
        )
        await self._connection.commit()