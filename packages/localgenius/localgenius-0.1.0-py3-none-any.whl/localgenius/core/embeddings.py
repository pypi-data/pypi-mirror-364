"""Embedding generation using OpenAI API."""

import asyncio
from typing import List, Optional
import numpy as np
from openai import AsyncOpenAI
import logging

from .config import EmbeddingConfig


logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages embedding generation using OpenAI API."""
    
    def __init__(self, api_key: str, config: EmbeddingConfig):
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        self.client = AsyncOpenAI(api_key=api_key)
        self.config = config
        
    async def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        try:
            # Add timeout and better error handling
            response = await asyncio.wait_for(
                self.client.embeddings.create(
                    model=self.config.model,
                    input=text
                ),
                timeout=30.0  # 30 second timeout
            )
            
            embedding = response.data[0].embedding
            return np.array(embedding, dtype=np.float32)
            
        except asyncio.TimeoutError:
            logger.error("OpenAI API request timed out after 30 seconds")
            raise Exception("OpenAI API request timed out. Check your internet connection and API key.")
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            if "api_key" in str(e).lower() or "unauthorized" in str(e).lower():
                raise Exception("Invalid OpenAI API key. Please check your OPENAI_API_KEY environment variable.")
            raise
            
    async def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts in batches."""
        embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i:i + self.config.batch_size]
            
            try:
                # logger.info(f"Generating embeddings for batch {i//self.config.batch_size + 1} ({len(batch)} texts)")
                
                response = await asyncio.wait_for(
                    self.client.embeddings.create(
                        model=self.config.model,
                        input=batch
                    ),
                    timeout=60.0  # 60 second timeout for batches
                )
                
                batch_embeddings = [
                    np.array(data.embedding, dtype=np.float32)
                    for data in response.data
                ]
                embeddings.extend(batch_embeddings)
                
                # Small delay to avoid rate limits
                if i + self.config.batch_size < len(texts):
                    await asyncio.sleep(0.1)
                    
            except asyncio.TimeoutError:
                logger.error(f"OpenAI API request timed out for batch {i//self.config.batch_size + 1}")
                raise Exception("OpenAI API request timed out. Check your internet connection and API key.")
            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i}: {e}")
                if "api_key" in str(e).lower() or "unauthorized" in str(e).lower():
                    raise Exception("Invalid OpenAI API key. Please check your OPENAI_API_KEY environment variable.")
                raise
                
        return embeddings
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap - simple and fast."""
        if len(text) <= self.config.chunk_size:
            return [text]
            
        chunks = []
        start = 0
        
        while start < len(text):
            # Simple chunking - just slice the text
            end = min(start + self.config.chunk_size, len(text))
            chunk = text[start:end]
            
            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk)
            
            # Move to next chunk with overlap
            start = end - self.config.chunk_overlap
            if start >= len(text) - self.config.chunk_overlap:
                break
                
        return chunks
    
    def chunk_by_tokens(self, text: str, encoding_name: str = "cl100k_base") -> List[str]:
        """Split text into chunks based on token count (more accurate for embeddings)."""
        try:
            import tiktoken
            encoding = tiktoken.get_encoding(encoding_name)
        except ImportError:
            logger.warning("tiktoken not installed, falling back to character-based chunking")
            return self.chunk_text(text)
            
        tokens = encoding.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = min(start + self.config.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            # Move with overlap
            start = end - self.config.chunk_overlap
            if start >= len(tokens) - self.config.chunk_overlap:
                break
                
        return chunks