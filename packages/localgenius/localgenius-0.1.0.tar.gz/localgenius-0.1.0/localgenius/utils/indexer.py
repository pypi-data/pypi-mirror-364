"""Document indexing functionality."""

import asyncio
import aiofiles
from pathlib import Path
from typing import List, Dict, Any
import mimetypes
from datetime import datetime
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.console import Console

from ..core.config import Settings, DataSource
from ..core.database import Database, Document
from ..core.embeddings import EmbeddingManager


console = Console()


class Indexer:
    """Handles document indexing and embedding generation."""
    
    def __init__(self, database: Database, embeddings: EmbeddingManager, settings: Settings):
        self.db = database
        self.embeddings = embeddings
        self.settings = settings
        
    async def index_source(self, source: DataSource) -> None:
        """Index all documents from a data source."""
        # Get all files matching patterns
        console.print(f"[cyan]Scanning {source.path} for files matching: {', '.join(source.file_patterns)}[/cyan]")
        files = self._get_files(source)
        
        if not files:
            console.print(f"[yellow]No files found in {source.path}[/yellow]")
            console.print(f"[yellow]File patterns: {source.file_patterns}[/yellow]")
            console.print(f"[yellow]Recursive: {source.recursive}[/yellow]")
            return
            
        console.print(f"[green]Found {len(files)} files to index[/green]")
        
        indexed_count = 0
        skipped_count = 0
        
        for i, file_path in enumerate(files, 1):
            console.print(f"\n[cyan]Processing file {i}/{len(files)}: {file_path.name}[/cyan]")
            try:
                await self._index_file(file_path, source)
                indexed_count += 1
            except Exception as e:
                console.print(f"[red]Error indexing {file_path}: {e}[/red]")
                skipped_count += 1
                import traceback
                traceback.print_exc()
                    
        console.print(f"[green]✓ Indexed {indexed_count} files[/green]")
        if skipped_count > 0:
            console.print(f"[yellow]⚠ Skipped {skipped_count} files due to errors[/yellow]")
                    
        # Update data source statistics
        await self.db.update_data_source_stats(str(source.path), source.name)
        
    def _get_files(self, source: DataSource) -> List[Path]:
        """Get all files matching the source patterns."""
        files = []
        
        for pattern in source.file_patterns:
            if source.recursive:
                matches = list(source.path.rglob(pattern))
            else:
                matches = list(source.path.glob(pattern))
            
            # Debug output
            if matches:
                console.print(f"[dim]  Pattern '{pattern}' matched {len(matches)} items[/dim]")
            
            files.extend(matches)
            
        # Filter out directories and return unique files
        unique_files = list(set(f for f in files if f.is_file()))
        console.print(f"[dim]  Total unique files: {len(unique_files)}[/dim]")
        return unique_files
        
    async def _index_file(self, file_path: Path, source: DataSource) -> None:
        """Index a single file."""
        # Read file content
        console.print(f"[dim]  Reading file: {file_path.name}[/dim]")
        content = await self._read_file(file_path)
        if not content or not content.strip():
            console.print(f"[dim]  Skipping empty file: {file_path.name}[/dim]")
            return
        
        console.print(f"[dim]  File size: {len(content)} characters[/dim]")
            
        # Chunk the content
        console.print(f"[dim]  Chunking content...[/dim]")
        chunks = self.embeddings.chunk_text(content)
        
        if not chunks:
            console.print(f"[dim]  No chunks generated for: {file_path.name}[/dim]")
            return
        
        # Generate embeddings for all chunks
        console.print(f"[dim]  Generating embeddings for {len(chunks)} chunks...[/dim]")
        
        try:
            embeddings = await self.embeddings.embed_texts(chunks)
            console.print(f"[dim]  Generated {len(embeddings)} embeddings[/dim]")
        except Exception as e:
            console.print(f"[red]  Failed to generate embeddings: {str(e)}[/red]")
            raise
        
        # Store in database
        console.print(f"[dim]  Storing in database...[/dim]")
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            document = Document(
                source_path=str(source.path),
                content=chunk,
                chunk_index=i,
                metadata={
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "mime_type": mimetypes.guess_type(str(file_path))[0],
                    "total_chunks": len(chunks),
                }
            )
            
            await self.db.add_document(document, embedding)
            
        console.print(f"[dim]  ✓ File indexed successfully[/dim]")
            
    async def _read_file(self, file_path: Path) -> str:
        """Read file content based on type."""
        mime_type = mimetypes.guess_type(str(file_path))[0]
        
        # Text files
        if mime_type and mime_type.startswith('text/'):
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return await f.read()
                
        # Common text file extensions
        text_extensions = {'.txt', '.md', '.rst', '.log', '.csv', '.json', '.xml', '.yaml', '.yml'}
        if file_path.suffix.lower() in text_extensions:
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return await f.read()
                
        # Code files
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r',
            '.m', '.mm', '.pl', '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat',
            '.html', '.css', '.scss', '.less', '.sql', '.lua', '.vim', '.el'
        }
        if file_path.suffix.lower() in code_extensions:
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return await f.read()
                
        # For now, skip other file types
        # In the future, we could add support for PDFs, DOCX, etc.
        return ""