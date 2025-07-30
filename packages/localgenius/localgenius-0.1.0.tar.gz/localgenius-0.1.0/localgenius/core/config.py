"""Configuration management for LocalGenius."""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DataSource(BaseModel):
    """Configuration for a data source."""
    path: Path
    name: str
    enabled: bool = True
    file_patterns: List[str] = Field(default_factory=lambda: [
        "*.txt", "*.md", "*.markdown", "*.rst", 
        "*.py", "*.js", "*.ts", "*.jsx", "*.tsx", 
        "*.java", "*.cpp", "*.c", "*.h", "*.hpp",
        "*.json", "*.yaml", "*.yml", "*.xml",
        "*.html", "*.css", "*.scss",
        "*.sh", "*.bash", "*.zsh",
        "*.go", "*.rs", "*.rb", "*.php"
    ])
    recursive: bool = True
    
    @validator("path")
    def validate_path(cls, v):
        path = Path(v) if not isinstance(v, Path) else v
        if not path.exists():
            raise ValueError(f"Path {path} does not exist")
        return path


class EmbeddingConfig(BaseModel):
    """Configuration for embeddings."""
    model: str = "text-embedding-ada-002"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    batch_size: int = 100


class DatabaseConfig(BaseModel):
    """Configuration for the database."""
    path: Path = Path.home() / ".localgenius" / "db" / "localgenius.db"
    vector_dimension: int = 1536  # OpenAI ada-002 dimension


class MCPConfig(BaseModel):
    """Configuration for the MCP server."""
    host: str = "localhost"
    port: int = 8765
    max_context_items: int = 10
    similarity_threshold: float = 0.7


class Settings(BaseSettings):
    """Main settings for LocalGenius."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # OpenAI API key from environment
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    
    # Configuration file path
    config_path: Path = Path.home() / ".localgenius" / "config.yaml"
    
    # Sub-configurations
    data_sources: List[DataSource] = Field(default_factory=list)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    
    # First run flag
    first_run: bool = True
    
    @classmethod
    def load_from_file(cls, config_path: Optional[Path] = None) -> "Settings":
        """Load settings from a YAML file."""
        settings = cls()
        
        if config_path:
            settings.config_path = config_path
            
        if settings.config_path.exists():
            with open(settings.config_path, "r") as f:
                config_data = yaml.safe_load(f) or {}
                
            # Update settings with file data
            if "data_sources" in config_data:
                # Filter out data sources with non-existent paths
                valid_sources = []
                for ds in config_data["data_sources"]:
                    try:
                        valid_sources.append(DataSource(**ds))
                    except ValueError as e:
                        # Skip data sources with invalid paths
                        print(f"Warning: Skipping data source with invalid path: {e}", file=__import__('sys').stderr)
                        continue
                settings.data_sources = valid_sources
            if "embedding" in config_data:
                settings.embedding = EmbeddingConfig(**config_data["embedding"])
            if "database" in config_data:
                settings.database = DatabaseConfig(**config_data["database"])
            if "mcp" in config_data:
                settings.mcp = MCPConfig(**config_data["mcp"])
            if "first_run" in config_data:
                settings.first_run = config_data["first_run"]
                
        return settings
    
    def save_to_file(self) -> None:
        """Save current settings to YAML file."""
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            "first_run": self.first_run,
            "data_sources": [
                {
                    "path": str(ds.path),
                    "name": ds.name,
                    "enabled": ds.enabled,
                    "file_patterns": ds.file_patterns,
                    "recursive": ds.recursive,
                }
                for ds in self.data_sources
            ],
            "embedding": self.embedding.model_dump(),
            "database": {
                "path": str(self.database.path),
                "vector_dimension": self.database.vector_dimension,
            },
            "mcp": self.mcp.model_dump(),
        }
        
        with open(self.config_path, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False)
    
    def add_data_source(self, path: Path, name: Optional[str] = None) -> None:
        """Add a new data source."""
        if name is None:
            name = path.name
            
        # Check if already exists
        for ds in self.data_sources:
            if ds.path == path:
                raise ValueError(f"Data source at {path} already exists")
                
        self.data_sources.append(DataSource(path=path, name=name))
        self.save_to_file()
    
    def remove_data_source(self, path: Path) -> None:
        """Remove a data source."""
        self.data_sources = [ds for ds in self.data_sources if ds.path != path]
        self.save_to_file()
    
    def get_active_data_sources(self) -> List[DataSource]:
        """Get all enabled data sources."""
        return [ds for ds in self.data_sources if ds.enabled]