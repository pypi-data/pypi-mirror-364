"""First-run onboarding flow using Rich library."""

import os
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.table import Table
from rich import print as rprint
import asyncio

from ..core.config import Settings
from ..core.database import Database


console = Console()


class OnboardingWizard:
    """Interactive onboarding wizard for first-time setup."""
    
    def __init__(self):
        self.settings = Settings()
        
    async def run(self) -> Settings:
        """Run the onboarding wizard."""
        console.clear()
        
        # Welcome message
        welcome_text = Text.from_markup(
            "[bold cyan]Welcome to LocalGenius![/bold cyan]\n\n"
            "Your personal MCP server for RAG-powered LLM interactions.\n\n"
            "This wizard will help you set up LocalGenius for the first time."
        )
        console.print(Panel(welcome_text, title="🧠 LocalGenius Setup", border_style="cyan"))
        console.print()
        
        # Check OpenAI API key
        await self._setup_openai_key()
        
        # Configure data sources
        await self._setup_data_sources()
        
        # Configure MCP server
        await self._setup_mcp_server()
        
        # Initialize database
        await self._initialize_database()
        
        # Save configuration
        self.settings.first_run = False
        self.settings.save_to_file()
        
        # Success message
        success_text = Text.from_markup(
            "[bold green]✓ Setup completed successfully![/bold green]\n\n"
            "LocalGenius is now configured and ready to use.\n\n"
            f"Configuration saved to: [cyan]{self.settings.config_path}[/cyan]\n"
            f"Database location: [cyan]{self.settings.database.path}[/cyan]\n\n"
            "Run [bold]localgenius --help[/bold] to see available commands."
        )
        console.print(Panel(success_text, title="🎉 Setup Complete", border_style="green"))
        
        return self.settings
        
    async def _setup_openai_key(self) -> None:
        """Set up OpenAI API key."""
        console.print("[bold]Step 1: OpenAI API Key[/bold]")
        console.print("LocalGenius uses OpenAI embeddings for semantic search.\n")
        
        if self.settings.openai_api_key:
            console.print(f"[green]✓[/green] OpenAI API key found in environment.")
        else:
            api_key = Prompt.ask(
                "Please enter your OpenAI API key",
                password=True,
                default=None
            )
            
            if api_key:
                # Save to environment file
                env_path = Path(".env")
                with open(env_path, "a") as f:
                    f.write(f"\nOPENAI_API_KEY={api_key}\n")
                console.print("[green]✓[/green] API key saved to .env file.")
                self.settings.openai_api_key = api_key
            else:
                console.print(
                    "[yellow]⚠[/yellow] No API key provided. "
                    "You'll need to set OPENAI_API_KEY environment variable later."
                )
        console.print()
        
    async def _setup_data_sources(self) -> None:
        """Configure initial data sources."""
        console.print("[bold]Step 2: Data Sources[/bold]")
        console.print("Add directories containing documents you want to index.\n")
        
        add_sources = Confirm.ask("Would you like to add data sources now?", default=True)
        
        if add_sources:
            while True:
                path_str = Prompt.ask(
                    "Enter path to directory",
                    default=str(Path.home() / "Documents")
                )
                
                path = Path(path_str).expanduser().resolve()
                
                if not path.exists():
                    console.print(f"[red]✗[/red] Path '{path}' does not exist.")
                    continue
                    
                if not path.is_dir():
                    console.print(f"[red]✗[/red] Path '{path}' is not a directory.")
                    continue
                    
                name = Prompt.ask(
                    "Enter a name for this data source",
                    default=path.name
                )
                
                try:
                    self.settings.add_data_source(path, name)
                    console.print(f"[green]✓[/green] Added data source: {name} ({path})")
                except ValueError as e:
                    console.print(f"[red]✗[/red] {e}")
                    
                add_more = Confirm.ask("Add another data source?", default=False)
                if not add_more:
                    break
        else:
            console.print(
                "[yellow]ℹ[/yellow] You can add data sources later using: "
                "[bold]localgenius add-source <path>[/bold]"
            )
        console.print()
        
    async def _setup_mcp_server(self) -> None:
        """Configure MCP server settings."""
        console.print("[bold]Step 3: MCP Server Configuration[/bold]")
        console.print("Configure the Model Context Protocol server.\n")
        
        # Show current settings
        table = Table(title="Current Settings")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Host", self.settings.mcp.host)
        table.add_row("Port", str(self.settings.mcp.port))
        table.add_row("Max Context Items", str(self.settings.mcp.max_context_items))
        table.add_row("Similarity Threshold", f"{self.settings.mcp.similarity_threshold:.2f}")
        
        console.print(table)
        console.print()
        
        customize = Confirm.ask("Would you like to customize these settings?", default=False)
        
        if customize:
            self.settings.mcp.host = Prompt.ask(
                "Host",
                default=self.settings.mcp.host
            )
            
            self.settings.mcp.port = int(Prompt.ask(
                "Port",
                default=str(self.settings.mcp.port)
            ))
            
            self.settings.mcp.max_context_items = int(Prompt.ask(
                "Max context items to return",
                default=str(self.settings.mcp.max_context_items)
            ))
            
            self.settings.mcp.similarity_threshold = float(Prompt.ask(
                "Similarity threshold (0.0-1.0)",
                default=f"{self.settings.mcp.similarity_threshold:.2f}"
            ))
            
            console.print("[green]✓[/green] MCP server settings updated.")
        console.print()
        
    async def _initialize_database(self) -> None:
        """Initialize the database."""
        console.print("[bold]Step 4: Database Initialization[/bold]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing database...", total=None)
            
            db = Database(
                self.settings.database.path,
                self.settings.database.vector_dimension
            )
            await db.initialize()
            await db.close()
            
            progress.update(task, completed=True)
            
        console.print("[green]✓[/green] Database initialized successfully.")
        console.print()


async def check_and_run_onboarding() -> Settings:
    """Check if onboarding is needed and run it."""
    settings = Settings.load_from_file()
    
    if settings.first_run:
        wizard = OnboardingWizard()
        return await wizard.run()
    
    return settings