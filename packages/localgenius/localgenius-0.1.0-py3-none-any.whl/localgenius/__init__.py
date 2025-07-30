"""LocalGenius - A personal MCP server for RAG-powered LLM interactions."""

__version__ = "0.1.0"
__author__ = "Marco Kotrotsos"

# Fix for OpenMP conflict on macOS with FAISS
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from .core.config import Settings
from .core.database import Database
from .core.embeddings import EmbeddingManager

__all__ = ["Settings", "Database", "EmbeddingManager"]