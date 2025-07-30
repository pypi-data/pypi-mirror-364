"""RAG (Retrieval-Augmented Generation) functionality."""

from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
import asyncio

from .database import Database
from .embeddings import EmbeddingManager
from .config import Settings


class RAGService:
    """Provides RAG functionality for question answering."""
    
    def __init__(self, settings: Settings, database: Database):
        self.settings = settings
        self.db = database
        self.embeddings = EmbeddingManager(settings.openai_api_key, settings.embedding)
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        
    async def ask(
        self, 
        query: str, 
        model: str = "gpt-4o",
        max_context_items: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ask a question using RAG."""
        # Use defaults from settings if not provided
        max_context_items = max_context_items or self.settings.mcp.max_context_items
        similarity_threshold = similarity_threshold or self.settings.mcp.similarity_threshold
        
        # Step 1: Generate embedding for the query
        query_embedding = await self.embeddings.embed_text(query)
        
        # Step 2: Search for relevant documents
        results = await self.db.search_similar(
            query_embedding, 
            k=max_context_items, 
            threshold=similarity_threshold
        )
        
        if not results:
            return {
                "query": query,
                "answer": "I couldn't find any relevant information in the indexed documents to answer your question.",
                "sources": [],
                "model": model
            }
        
        # Step 3: Format context from results
        context_parts = []
        sources = []
        
        for doc, score in results:
            context_parts.append(f"[Source: {doc.metadata.get('file_name', 'Unknown')}]\n{doc.content}")
            sources.append({
                "file": doc.metadata.get('file_path', doc.source_path),
                "chunk": doc.chunk_index,
                "similarity": round(score, 3)
            })
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Step 4: Create the prompt
        if not system_prompt:
            system_prompt = self.settings.prompts.system_prompt
        
        user_content = self.settings.prompts.user_prompt_template.format(
            context=context,
            query=query
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        # Step 5: Generate response using OpenAI
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=self.settings.prompts.temperature,
                max_tokens=self.settings.prompts.max_tokens
            )
            
            answer = response.choices[0].message.content
            
            return {
                "query": query,
                "answer": answer,
                "sources": sources,
                "model": model,
                "context_used": len(results),
                "tokens_used": response.usage.total_tokens if response.usage else None
            }
            
        except Exception as e:
            return {
                "query": query,
                "answer": f"Error generating response: {str(e)}",
                "sources": sources,
                "model": model,
                "error": str(e)
            }
    
    async def ask_with_streaming(
        self,
        query: str,
        model: str = "gpt-4o",
        max_context_items: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        system_prompt: Optional[str] = None
    ):
        """Ask a question using RAG with streaming response."""
        # Use defaults from settings if not provided
        max_context_items = max_context_items or self.settings.mcp.max_context_items
        similarity_threshold = similarity_threshold or self.settings.mcp.similarity_threshold
        
        # Step 1: Generate embedding for the query
        query_embedding = await self.embeddings.embed_text(query)
        
        # Step 2: Search for relevant documents
        results = await self.db.search_similar(
            query_embedding, 
            k=max_context_items, 
            threshold=similarity_threshold
        )
        
        if not results:
            yield {
                "type": "error",
                "content": "No relevant documents found."
            }
            return
        
        # Step 3: Format context
        context_parts = []
        sources = []
        
        for doc, score in results:
            context_parts.append(f"[Source: {doc.metadata.get('file_name', 'Unknown')}]\n{doc.content}")
            sources.append({
                "file": doc.metadata.get('file_path', doc.source_path),
                "chunk": doc.chunk_index,
                "similarity": round(score, 3)
            })
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Yield sources first
        yield {
            "type": "sources",
            "content": sources
        }
        
        # Step 4: Create the prompt
        if not system_prompt:
            system_prompt = self.settings.prompts.system_prompt
        
        user_content = self.settings.prompts.user_prompt_template.format(
            context=context,
            query=query
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        # Step 5: Stream response
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=self.settings.prompts.temperature,
                max_tokens=self.settings.prompts.max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield {
                        "type": "content",
                        "content": chunk.choices[0].delta.content
                    }
                    
        except Exception as e:
            yield {
                "type": "error",
                "content": f"Error generating response: {str(e)}"
            }