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
        """Split text into chunks with overlap - respects separator boundaries."""
        # Check if we should use separator-based chunking
        if self.config.chunk_separator and self.config.chunk_separator in text:
            return self._chunk_with_separator(text)
        else:
            # For character-based chunking, only return as single chunk if small enough
            if len(text) <= self.config.chunk_size:
                return [text]
            # Fallback to simple character-based chunking
            return self._chunk_by_characters(text)
    
    def _chunk_with_separator(self, text: str) -> List[str]:
        """Split text using separator, with different strategies."""
        separator = self.config.chunk_separator
        # Handle escaped characters like \\n
        separator = separator.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r')
        
        # Split by separator first
        segments = text.split(separator)
        
        # Choose strategy
        strategy = getattr(self.config, 'chunk_strategy', 'size_first')
        
        if strategy == 'separator_strict':
            return self._chunk_separator_strict(segments, separator)
        else:
            return self._chunk_size_first(segments, separator)
    
    def _chunk_separator_strict(self, segments: List[str], separator: str) -> List[str]:
        """Always split on separator, only combine oversized segments."""
        chunks = []
        
        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue
                
            # If segment is within size limit, add as-is
            if len(segment) <= self.config.chunk_size:
                chunks.append(segment)
            else:
                # Split oversized segment by characters (without overlap for strict mode)
                oversized_chunks = self._chunk_by_characters_no_overlap(segment)
                chunks.extend(oversized_chunks)
        
        # In separator-strict mode, do NOT apply overlap
        # The user wants clean separation at separator boundaries
        return [chunk for chunk in chunks if chunk.strip()]
    
    def _chunk_size_first(self, segments: List[str], separator: str) -> List[str]:
        """Combine segments until size limit, respecting separator boundaries."""
        chunks = []
        current_chunk = ""
        
        for segment in segments:
            # If adding this segment would exceed chunk size, finalize current chunk
            potential_chunk = current_chunk + (separator if current_chunk else "") + segment
            
            if len(potential_chunk) > self.config.chunk_size and current_chunk:
                # Add current chunk and start new one
                chunks.append(current_chunk.strip())
                current_chunk = segment
            else:
                current_chunk = potential_chunk
            
            # If even a single segment is too long, split it by characters
            if len(current_chunk) > self.config.chunk_size:
                if current_chunk.strip():
                    # Split oversized segment and add pieces
                    oversized_chunks = self._chunk_by_characters(current_chunk)
                    chunks.extend(oversized_chunks[:-1])  # Add all but the last
                    current_chunk = oversized_chunks[-1] if oversized_chunks else ""
        
        # Add the final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Apply overlap if we have multiple chunks
        if len(chunks) > 1 and self.config.chunk_overlap > 0:
            chunks = self._apply_overlap(chunks)
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def _chunk_by_characters(self, text: str) -> List[str]:
        """Simple character-based chunking with overlap."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.config.chunk_size, len(text))
            chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk)
            
            start = end - self.config.chunk_overlap
            if start >= len(text) - self.config.chunk_overlap:
                break
                
        return chunks
    
    def _chunk_by_characters_no_overlap(self, text: str) -> List[str]:
        """Simple character-based chunking without overlap (for strict mode)."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.config.chunk_size, len(text))
            chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk)
            
            start = end  # No overlap
                
        return chunks
    
    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """Apply overlap between chunks for better context preservation."""
        if len(chunks) <= 1 or self.config.chunk_overlap <= 0:
            return chunks
            
        overlapped_chunks = [chunks[0]]  # First chunk as-is
        
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i-1]
            current_chunk = chunks[i]
            
            # Get overlap from end of previous chunk
            overlap_text = prev_chunk[-self.config.chunk_overlap:] if len(prev_chunk) > self.config.chunk_overlap else prev_chunk
            
            # Prepend overlap to current chunk if it doesn't already contain it
            if not current_chunk.startswith(overlap_text):
                overlapped_chunk = overlap_text + " " + current_chunk
            else:
                overlapped_chunk = current_chunk
                
            overlapped_chunks.append(overlapped_chunk)
        
        return overlapped_chunks
    
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