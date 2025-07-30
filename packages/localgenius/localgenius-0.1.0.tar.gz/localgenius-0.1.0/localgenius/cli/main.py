"""Main CLI entry point for LocalGenius."""

# Fix for OpenMP conflict on macOS with FAISS
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .onboarding import check_and_run_onboarding
from ..core.config import Settings
from ..core.database import Database
from ..core.embeddings import EmbeddingManager
from ..core.rag import RAGService
# HTTP server functionality removed - use MCP server instead
from ..utils.indexer import Indexer


console = Console()


@click.group()
@click.pass_context
def cli(ctx):
    """LocalGenius - Personal MCP server for RAG-powered LLM interactions."""
    # Load settings (will be available to all commands)
    ctx.ensure_object(dict)
    ctx.obj['settings'] = Settings.load_from_file()


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize LocalGenius (first-run setup)."""
    settings = asyncio.run(check_and_run_onboarding())
    ctx.obj['settings'] = settings


@cli.command()
@click.option('--claude', is_flag=True, help='Install MCP server in Claude Desktop')
@click.pass_context
def install(ctx, claude: bool):
    """Install LocalGenius integrations."""
    if claude:
        asyncio.run(_install_claude_mcp(ctx.obj['settings']))
    else:
        console.print("Please specify an integration to install:")
        console.print("  --claude    Install MCP server in Claude Desktop")


@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('--name', '-n', help='Name for the data source')
@click.option('--index', '-i', is_flag=True, help='Index the data source immediately')
@click.pass_context
def add_source(ctx, path: Path, name: Optional[str], index: bool):
    """Add a new data source."""
    settings: Settings = ctx.obj['settings']
    
    try:
        settings.add_data_source(path.resolve(), name)
        console.print(f"[green]✓[/green] Added data source: {name or path.name} ({path})")
        
        if index:
            console.print("Indexing data source...")
            asyncio.run(_index_source(settings, path.resolve()))
            
    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
        raise click.Exit(1)


@cli.command()
@click.argument('path', type=click.Path(path_type=Path))
@click.pass_context
def remove_source(ctx, path: Path):
    """Remove a data source."""
    settings: Settings = ctx.obj['settings']
    
    try:
        settings.remove_data_source(path.resolve())
        console.print(f"[green]✓[/green] Removed data source: {path}")
        
        # Also remove from database
        asyncio.run(_remove_source_from_db(settings, path.resolve()))
        
    except ValueError:
        console.print(f"[red]✗[/red] Data source not found: {path}")
        raise click.Exit(1)


@cli.command()
@click.pass_context
def list_sources(ctx):
    """List all data sources."""
    settings: Settings = ctx.obj['settings']
    
    if not settings.data_sources:
        console.print("[yellow]No data sources configured.[/yellow]")
        console.print("Use [bold]localgenius add-source <path>[/bold] to add one.")
        return
        
    table = Table(title="Data Sources")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Patterns", style="magenta")
    
    for source in settings.data_sources:
        status = "✓ Enabled" if source.enabled else "✗ Disabled"
        patterns = ", ".join(source.file_patterns)
        table.add_row(source.name, str(source.path), status, patterns)
        
    console.print(table)


@cli.command()
@click.option('--source', '-s', type=click.Path(path_type=Path), help='Index specific source')
@click.option('--force', '-f', is_flag=True, help='Force re-indexing')
@click.option('--show', is_flag=True, help='Show detailed index statistics and contents')
@click.pass_context
def index(ctx, source: Optional[Path], force: bool, show: bool):
    """Index data sources or show index contents."""
    settings: Settings = ctx.obj['settings']
    
    if show:
        # Show index statistics and contents
        asyncio.run(_show_index_details(settings))
        return
    
    if not settings.openai_api_key:
        console.print("[red]✗[/red] OpenAI API key not configured.")
        console.print("Set OPENAI_API_KEY environment variable or run [bold]localgenius init[/bold]")
        raise click.Exit(1)
        
    sources_to_index = []
    
    if source:
        # Find specific source
        source = source.resolve()
        for ds in settings.data_sources:
            if ds.path == source:
                sources_to_index.append(ds)
                break
        else:
            console.print(f"[red]✗[/red] Data source not found: {source}")
            raise click.Exit(1)
    else:
        # Index all enabled sources
        sources_to_index = settings.get_active_data_sources()
        
    if not sources_to_index:
        console.print("[yellow]No data sources to index.[/yellow]")
        return
        
    console.print(f"Indexing {len(sources_to_index)} data source(s)...")
    asyncio.run(_index_sources(settings, sources_to_index, force))


@cli.command()
@click.option('--mcp', is_flag=True, default=True, help='Run as MCP server (default)')
@click.pass_context
def serve(ctx, mcp: bool):
    """Start the MCP server for Claude Desktop integration."""
    settings: Settings = ctx.obj['settings']
        
    # In MCP mode, suppress all console output as it interferes with JSON-RPC protocol
    import os
    import sys
    
    # Redirect stdout to stderr to prevent interfering with MCP protocol
    old_stdout = sys.stdout
    sys.stdout = sys.stderr
    
    try:
        asyncio.run(_run_mcp_server(settings))
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout = old_stdout


@cli.command()
@click.pass_context
def status(ctx):
    """Show LocalGenius status and statistics."""
    settings: Settings = ctx.obj['settings']
    
    # Configuration status
    config_table = Table(title="Configuration")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    
    config_table.add_row("Config Path", str(settings.config_path))
    config_table.add_row("Database Path", str(settings.database.path))
    config_table.add_row("OpenAI API Key", "✓ Configured" if settings.openai_api_key else "✗ Not configured")
    config_table.add_row("MCP Server", f"{settings.mcp.host}:{settings.mcp.port}")
    
    console.print(config_table)
    console.print()
    
    # Database statistics
    stats = asyncio.run(_get_db_stats(settings))
    
    stats_table = Table(title="Database Statistics")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")
    
    stats_table.add_row("Total Documents", str(stats["total_documents"]))
    stats_table.add_row("Total Embeddings", str(stats["total_embeddings"]))
    stats_table.add_row("Vector Dimension", str(stats["vector_dimension"]))
    
    console.print(stats_table)
    
    if stats["sources"]:
        console.print()
        sources_table = Table(title="Indexed Sources")
        sources_table.add_column("Source", style="cyan")
        sources_table.add_column("Documents", style="green")
        
        for source, count in stats["sources"].items():
            sources_table.add_row(source, str(count))
            
        console.print(sources_table)


@cli.command()
@click.argument('query')
@click.option('--limit', '-l', type=int, default=5, help='Number of results')
@click.option('--threshold', '-t', type=float, default=0.7, help='Similarity threshold')
@click.pass_context
def search(ctx, query: str, limit: int, threshold: float):
    """Search for similar content."""
    settings: Settings = ctx.obj['settings']
    
    if not settings.openai_api_key:
        console.print("[red]✗[/red] OpenAI API key not configured.")
        raise click.Exit(1)
        
    results = asyncio.run(_search_content(settings, query, limit, threshold))
    
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return
        
    for i, (doc, score) in enumerate(results, 1):
        console.print(f"\n[bold cyan]Result {i}[/bold cyan] (similarity: {score:.2f})")
        console.print(f"[green]Source:[/green] {doc.source_path}")
        console.print(f"[green]Chunk:[/green] {doc.chunk_index}")
        console.print(f"[dim]{doc.content[:200]}...[/dim]")


@cli.command()
@click.argument('question')
@click.option('--model', '-m', default='gpt-4o', help='OpenAI model to use')
@click.option('--limit', '-l', type=int, help='Max context items')
@click.option('--threshold', '-t', type=float, help='Similarity threshold')
@click.option('--stream', '-s', is_flag=True, help='Stream the response')
@click.pass_context
def ask(ctx, question: str, model: str, limit: Optional[int], threshold: Optional[float], stream: bool):
    """Ask a question using RAG (Retrieval-Augmented Generation)."""
    settings: Settings = ctx.obj['settings']
    
    if not settings.openai_api_key:
        console.print("[red]✗[/red] OpenAI API key not configured.")
        raise click.Exit(1)
        
    console.print(f"[cyan]Question:[/cyan] {question}\n")
    
    if stream:
        asyncio.run(_ask_streaming(settings, question, model, limit, threshold))
    else:
        result = asyncio.run(_ask_question(settings, question, model, limit, threshold))
        
        # Display sources
        if result.get("sources"):
            console.print("[bold]Sources used:[/bold]")
            for source in result["sources"]:
                console.print(f"  • {source['file']} (chunk {source['chunk']}, similarity: {source['similarity']})")
            console.print()
        
        # Display answer
        console.print("[bold]Answer:[/bold]")
        console.print(result["answer"])
        
        # Display metadata
        if result.get("tokens_used"):
            console.print(f"\n[dim]Model: {result['model']}, Tokens: {result['tokens_used']}, Context items: {result.get('context_used', 0)}[/dim]")


# Async helper functions

async def _index_source(settings: Settings, source_path: Path):
    """Index a single data source."""
    from ..utils.indexer import Indexer
    
    db = Database(settings.database.path, settings.database.vector_dimension)
    await db.initialize()
    
    embeddings = EmbeddingManager(settings.openai_api_key, settings.embedding)
    indexer = Indexer(db, embeddings, settings)
    
    # Find the data source config
    for ds in settings.data_sources:
        if ds.path == source_path:
            await indexer.index_source(ds)
            break
            
    await db.close()


async def _index_sources(settings: Settings, sources, force: bool):
    """Index multiple data sources."""
    from ..utils.indexer import Indexer
    
    try:
        db = Database(settings.database.path, settings.database.vector_dimension)
        await db.initialize()
        
        embeddings = EmbeddingManager(settings.openai_api_key, settings.embedding)
        indexer = Indexer(db, embeddings, settings)
        
        for source in sources:
            console.print(f"\n[bold]Indexing: {source.name}[/bold]")
            console.print(f"Path: {source.path}")
            
            if force:
                console.print("[yellow]Force mode: removing existing documents...[/yellow]")
                # Remove existing documents
                await db.delete_documents_by_source(str(source.path))
                
            await indexer.index_source(source)
            
        await db.close()
        console.print("\n[green]✓[/green] Indexing complete.")
        
    except Exception as e:
        console.print(f"\n[red]✗ Indexing failed: {str(e)}[/red]")
        if "api_key" in str(e).lower():
            console.print("[yellow]Make sure your OpenAI API key is correctly set.[/yellow]")
        raise click.Exit(1)


async def _remove_source_from_db(settings: Settings, source_path: Path):
    """Remove source documents from database."""
    db = Database(settings.database.path, settings.database.vector_dimension)
    await db.initialize()
    await db.delete_documents_by_source(str(source_path))
    await db.close()


# HTTP server functionality removed - use MCP server instead


async def _run_mcp_server(settings: Settings):
    """Run the MCP server."""
    # Import and run the FastMCP server directly
    from ..mcp.fastmcp_server import main as run_fastmcp
    
    # FastMCP handles its own event loop, so we need to run it in sync context
    await asyncio.get_event_loop().run_in_executor(None, run_fastmcp)


async def _get_db_stats(settings: Settings):
    """Get database statistics."""
    db = Database(settings.database.path, settings.database.vector_dimension)
    await db.initialize()
    stats = await db.get_statistics()
    await db.close()
    return stats


async def _search_content(settings: Settings, query: str, limit: int, threshold: float):
    """Search for similar content."""
    db = Database(settings.database.path, settings.database.vector_dimension)
    await db.initialize()
    
    embeddings = EmbeddingManager(settings.openai_api_key, settings.embedding)
    query_embedding = await embeddings.embed_text(query)
    
    results = await db.search_similar(query_embedding, limit, threshold)
    
    await db.close()
    return results


async def _ask_question(settings: Settings, question: str, model: str, limit: Optional[int], threshold: Optional[float]):
    """Ask a question using RAG."""
    db = Database(settings.database.path, settings.database.vector_dimension)
    await db.initialize()
    
    rag = RAGService(settings, db)
    result = await rag.ask(
        query=question,
        model=model,
        max_context_items=limit,
        similarity_threshold=threshold
    )
    
    await db.close()
    return result


async def _ask_streaming(settings: Settings, question: str, model: str, limit: Optional[int], threshold: Optional[float]):
    """Ask a question with streaming response."""
    db = Database(settings.database.path, settings.database.vector_dimension)
    await db.initialize()
    
    rag = RAGService(settings, db)
    
    sources_shown = False
    console.print("[bold]Answer:[/bold]")
    
    async for chunk in rag.ask_with_streaming(
        query=question,
        model=model,
        max_context_items=limit,
        similarity_threshold=threshold
    ):
        if chunk["type"] == "sources" and not sources_shown:
            console.print("[bold]Sources used:[/bold]")
            for source in chunk["content"]:
                console.print(f"  • {source['file']} (chunk {source['chunk']}, similarity: {source['similarity']})")
            console.print()
            sources_shown = True
        elif chunk["type"] == "content":
            console.print(chunk["content"], end="")
        elif chunk["type"] == "error":
            console.print(f"\n[red]Error: {chunk['content']}[/red]")
    
    console.print()  # New line at the end
    await db.close()


async def _install_claude_mcp(settings: Settings):
    """Install LocalGenius MCP server in Claude Desktop."""
    import json
    from pathlib import Path
    import shutil
    
    console.print("[bold]Installing LocalGenius MCP server in Claude Desktop[/bold]\n")
    
    # Detect OS and set config path
    if sys.platform == "darwin":  # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    elif sys.platform == "linux":
        config_dir = Path.home() / ".config" / "Claude"
    elif sys.platform == "win32":
        config_dir = Path(os.environ.get("APPDATA", "")) / "Claude"
    else:
        console.print(f"[red]✗[/red] Unsupported platform: {sys.platform}")
        return
        
    config_file = config_dir / "claude_desktop_config.json"
    
    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Get the project directory
    project_dir = Path(__file__).parent.parent.parent
    mcp_script = project_dir / "run-mcp-server.sh"
    
    # Create run-mcp-server.sh if it doesn't exist
    if not mcp_script.exists():
        console.print("[yellow]Creating run-mcp-server.sh...[/yellow]")
        script_content = f'''#!/bin/bash
# MCP Server launcher for LocalGenius

# Set up environment
export PYTHONPATH="{project_dir}:$PYTHONPATH"

# Use the Python that has LocalGenius installed
PYTHON="{sys.executable}"

# Run the FastMCP server
exec "$PYTHON" "{project_dir}/localgenius/mcp/fastmcp_server.py"
'''
        mcp_script.write_text(script_content)
        mcp_script.chmod(0o755)
        console.print(f"[green]✓[/green] Created {mcp_script}")
    
    # Prepare the MCP server configuration
    mcp_config = {
        "command": str(mcp_script),
        "args": [],
        "env": {
            "OPENAI_API_KEY": settings.openai_api_key or "${OPENAI_API_KEY}"
        }
    }
    
    # Load existing config or create new one
    if config_file.exists():
        console.print(f"[green]✓[/green] Found existing Claude config")
        # Backup existing config
        backup_file = config_file.with_suffix(".json.backup")
        shutil.copy2(config_file, backup_file)
        console.print(f"[dim]  Backed up to {backup_file}[/dim]")
        
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        console.print("[yellow]Creating new Claude config[/yellow]")
        config = {}
    
    # Add or update LocalGenius MCP server
    if "mcpServers" not in config:
        config["mcpServers"] = {}
        
    if "localgenius" in config["mcpServers"]:
        console.print("[yellow]⚠ LocalGenius already configured, updating...[/yellow]")
    
    config["mcpServers"]["localgenius"] = mcp_config
    
    # Write updated config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    console.print(f"[green]✓[/green] Updated Claude config: {config_file}")
    
    # Show summary
    console.print("\n[bold green]Installation complete![/bold green]")
    console.print("\nLocalGenius MCP server has been added to Claude Desktop.")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Make sure you've indexed some documents: [cyan]localgenius index[/cyan]")
    console.print("2. Completely quit Claude Desktop (Cmd+Q on Mac)")
    console.print("3. Restart Claude Desktop")
    console.print("4. Look for the MCP icon (🧩) in the text input area")
    console.print("\n[bold]You can now ask Claude:[/bold]")
    console.print('  • "Search my documents for X"')
    console.print('  • "What do my files say about Y?"')
    console.print('  • "Show me the LocalGenius status"')


async def _show_index_details(settings: Settings):
    """Show detailed index statistics and contents."""
    db = Database(settings.database.path, settings.database.vector_dimension)
    await db.initialize()
    
    # Get basic statistics
    stats = await db.get_statistics()
    
    # Display overview
    console.print("[bold]LocalGenius Index Details[/bold]\n")
    
    # Summary table
    summary_table = Table(title="Index Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")
    
    summary_table.add_row("Total Documents", str(stats["total_documents"]))
    summary_table.add_row("Total Embeddings", str(stats["total_embeddings"]))
    summary_table.add_row("Vector Dimension", str(stats["vector_dimension"]))
    summary_table.add_row("Database Location", str(settings.database.path))
    summary_table.add_row("Index Size", f"{settings.database.path.stat().st_size / 1024 / 1024:.2f} MB" if settings.database.path.exists() else "N/A")
    
    console.print(summary_table)
    console.print()
    
    # Sources breakdown
    if stats["sources"]:
        sources_table = Table(title="Indexed Sources")
        sources_table.add_column("Source Path", style="cyan")
        sources_table.add_column("Documents", style="green")
        sources_table.add_column("Percentage", style="yellow")
        
        total_docs = stats["total_documents"]
        for source, count in sorted(stats["sources"].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_docs * 100) if total_docs > 0 else 0
            sources_table.add_row(source, str(count), f"{percentage:.1f}%")
            
        console.print(sources_table)
        console.print()
    
    # Sample documents
    console.print("[bold]Sample Indexed Documents:[/bold]")
    
    # Get a few sample documents
    cursor = await db._connection.execute(
        """
        SELECT source_path, content, chunk_index, metadata 
        FROM documents 
        ORDER BY RANDOM() 
        LIMIT 5
        """
    )
    samples = await cursor.fetchall()
    
    for i, (source, content, chunk_idx, metadata_str) in enumerate(samples, 1):
        metadata = json.loads(metadata_str) if metadata_str else {}
        console.print(f"\n[cyan]Sample {i}:[/cyan]")
        console.print(f"  Source: {metadata.get('file_name', 'Unknown')}")
        console.print(f"  Chunk: {chunk_idx}/{metadata.get('total_chunks', '?')}")
        console.print(f"  Preview: [dim]{content[:150]}...[/dim]")
    
    # File type statistics
    console.print("\n[bold]File Types Indexed:[/bold]")
    
    cursor = await db._connection.execute(
        """
        SELECT metadata FROM documents
        """
    )
    all_metadata = await cursor.fetchall()
    
    file_types = {}
    for (metadata_str,) in all_metadata:
        if metadata_str:
            metadata = json.loads(metadata_str)
            file_name = metadata.get('file_name', '')
            if file_name:
                ext = Path(file_name).suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
    
    if file_types:
        type_table = Table()
        type_table.add_column("File Type", style="cyan")
        type_table.add_column("Count", style="green")
        
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            type_table.add_row(ext or "(no extension)", str(count))
            
        console.print(type_table)
    
    await db.close()


if __name__ == "__main__":
    cli()