#!/usr/bin/env python3
"""LocalGenius MCP server using FastMCP."""

import os
import sys

# Fix for OpenMP conflict on macOS with FAISS
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import asyncio
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from localgenius.core.config import Settings
from localgenius.core.database import Database
from localgenius.core.embeddings import EmbeddingManager
from localgenius.core.rag import RAGService

# Create FastMCP server instance
mcp = FastMCP("LocalGenius")

# Global instances (will be initialized on startup)
db: Database = None
rag: RAGService = None
embeddings: EmbeddingManager = None
settings: Settings = None


@mcp.tool()
async def search(query: str, limit: int = 5, threshold: float = 0.7) -> str:
    """Search for relevant content in indexed documents.
    
    Args:
        query: The search query
        limit: Maximum number of results (default: 5)
        threshold: Similarity threshold 0-1 (default: 0.7)
    
    Returns:
        Search results with similarity scores
    """
    global embeddings, db
    
    if not embeddings or not db:
        return "Error: Service not initialized"
    
    try:
        # Generate embedding for query
        query_embedding = await embeddings.embed_text(query)
        
        # Search similar documents
        results = await db.search_similar(query_embedding, limit, threshold)
        
        if not results:
            return "No matching documents found."
        
        # Format results
        output = f"Found {len(results)} matching documents:\n\n"
        
        for i, (doc, score) in enumerate(results, 1):
            source = doc.metadata.get("file_name", "Unknown")
            output += f"**Result {i}** (similarity: {score:.2f})\n"
            output += f"Source: {source} (chunk {doc.chunk_index})\n"
            output += f"Content: {doc.content[:300]}...\n\n"
        
        return output
        
    except Exception as e:
        return f"Error performing search: {str(e)}"


@mcp.tool()
async def ask(question: str, model: str = "gpt-4o") -> str:
    """Ask a question and get an AI-generated answer based on indexed documents.
    
    Args:
        question: The question to ask
        model: OpenAI model to use (default: gpt-4o)
    
    Returns:
        AI-generated answer with source citations
    """
    global rag, settings
    
    if not rag:
        return "Error: RAG service not initialized"
    
    try:
        # Use RAG to answer question
        result = await rag.ask(query=question, model=model)
        
        # If MCP prompt processing is enabled, apply custom prompts
        if settings and settings.prompts.use_for_mcp:
            processed_answer = await _apply_mcp_prompts(result["answer"], question, model)
            result["answer"] = processed_answer
        
        # Format response
        output = result["answer"] + "\n\n**Sources:**\n"
        
        for source in result.get("sources", []):
            output += f"- {source['file']} (chunk {source['chunk']}, similarity: {source['similarity']})\n"
        
        if result.get("tokens_used"):
            output += f"\n*Model: {model}, Tokens: {result['tokens_used']}*"
        
        return output
        
    except Exception as e:
        return f"Error generating answer: {str(e)}"


async def _apply_mcp_prompts(original_answer: str, question: str, model: str) -> str:
    """Apply custom MCP prompt processing to refine the answer."""
    global settings
    
    if not settings or not settings.openai_api_key:
        return original_answer
    
    try:
        import openai
        
        # Create OpenAI client
        client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        
        # Format the user prompt with the original answer as context
        user_content = settings.prompts.user_prompt_template.format(
            context=f"Original Answer: {original_answer}",
            query=f"Please refine and improve this answer to the question: {question}"
        )
        
        # Call OpenAI with custom prompts
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": settings.prompts.system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=settings.prompts.temperature,
            max_tokens=settings.prompts.max_tokens
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # If prompt processing fails, return original answer
        print(f"MCP prompt processing failed: {e}", file=sys.stderr)
        return original_answer


@mcp.tool()
async def status() -> str:
    """Get the status of the LocalGenius index.
    
    Returns:
        Statistics about indexed documents and sources
    """
    global db
    
    if not db:
        return "Error: Database not initialized"
    
    try:
        stats = await db.get_statistics()
        
        output = "**LocalGenius Status**\n\n"
        output += f"Total documents: {stats['total_documents']}\n"
        output += f"Total embeddings: {stats['total_embeddings']}\n"
        output += f"Vector dimension: {stats['vector_dimension']}\n\n"
        
        if stats["sources"]:
            output += "**Indexed Sources:**\n"
            for source, count in stats["sources"].items():
                output += f"- {source}: {count} documents\n"
        else:
            output += "No sources indexed yet.\n"
        
        return output
        
    except Exception as e:
        return f"Error getting status: {str(e)}"


async def initialize_services():
    """Initialize database and services."""
    global db, rag, embeddings, settings
    
    # Load settings
    settings = Settings.load_from_file()
    
    # Initialize database
    db = Database(settings.database.path, settings.database.vector_dimension)
    await db.initialize()
    
    # Initialize services if API key is available
    if settings.openai_api_key:
        embeddings = EmbeddingManager(settings.openai_api_key, settings.embedding)
        rag = RAGService(settings, db)
    else:
        sys.stderr.write("Warning: OpenAI API key not configured. Some features will be limited.\n")


async def cleanup_services():
    """Clean up database connections."""
    global db
    if db:
        await db.close()


def main():
    """Main entry point for MCP server."""
    # Initialize services in a separate async function
    async def setup():
        await initialize_services()
    
    # Run setup
    asyncio.run(setup())
    
    try:
        # Run the MCP server (this creates its own event loop)
        mcp.run()
    finally:
        # Clean up
        async def cleanup():
            await cleanup_services()
        asyncio.run(cleanup())


if __name__ == "__main__":
    # Run the server
    main()