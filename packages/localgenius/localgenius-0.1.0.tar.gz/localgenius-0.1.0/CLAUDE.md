# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LocalGenius is a Python CLI application for managing a local MCP (Model Context Protocol) server used as a context/datasource for LLMs. It provides RAG (Retrieval-Augmented Generation) capabilities through semantic search.

## Commands

### Installation and Setup
```bash
# Install in development mode
pip install -e .

# First run (will trigger onboarding wizard)
localgenius init

# Set up OpenAI API key (required for embeddings)
export OPENAI_API_KEY="your-api-key"
```

### CLI Commands
```bash
# Initialize/onboarding
localgenius init

# Install integrations
localgenius install --claude         # Auto-configure Claude Desktop

# Manage data sources
localgenius add-source /path/to/documents --name "My Docs" --index
localgenius remove-source /path/to/documents
localgenius list-sources

# Index documents
localgenius index                    # Index all enabled sources
localgenius index --source /path     # Index specific source
localgenius index --force           # Force re-indexing
localgenius index --show            # Show detailed index statistics

# Search (find similar content)
localgenius search "your query" --limit 5 --threshold 0.7

# Ask questions using RAG (Retrieval-Augmented Generation)
localgenius ask "What is the main topic of the documents?"
localgenius ask "Explain the architecture" --model gpt-4
localgenius ask "How does X work?" --stream  # Stream the response

# Run MCP server
localgenius serve --host localhost --port 8765

# Check status
localgenius status
```

## Architecture

### Core Components
- **CLI Framework**: Click with Rich for terminal UI
- **Configuration**: Pydantic settings with YAML config file at `~/.localgenius/config.yaml`
- **Database**: SQLite with FAISS for vector operations
- **Embeddings**: OpenAI text-embedding-ada-002 model
- **MCP Server**: Provides tools and resources for LLM integration

### Project Structure
```
localgenius/
├── cli/
│   ├── main.py         # CLI entry point and commands
│   └── onboarding.py   # First-run wizard with Rich UI
├── core/
│   ├── config.py       # Pydantic settings and configuration
│   ├── database.py     # SQLite + FAISS database management
│   └── embeddings.py   # OpenAI embedding generation
├── mcp/
│   └── server.py       # MCP server implementation
└── utils/
    └── indexer.py      # Document indexing logic
```

### Data Flow
1. Documents are indexed from configured data sources
2. Text is chunked with configurable size and overlap
3. OpenAI API generates embeddings for each chunk
4. Embeddings stored in FAISS index, metadata in SQLite
5. MCP server provides search tools for LLMs
6. Semantic search returns relevant context based on similarity

## Key Implementation Details

- **Async Operations**: Uses asyncio, aiofiles, and aiosqlite
- **Batch Processing**: Embeddings generated in configurable batches
- **Text Chunking**: Fast chunking with configurable size and overlap
- **File Support**: Handles text, markdown, code files, and common formats
- **RAG Service**: Full Retrieval-Augmented Generation pipeline
  - Semantic search for relevant context
  - Context formatting with source attribution
  - LLM-based answer generation
- **MCP Tools**: 
  - `search`: Query-based semantic search
  - `get_context`: Topic-based context retrieval
  - `ask`: RAG-powered question answering
- **Configuration**: First-run creates config at `~/.localgenius/config.yaml`

## Claude Desktop Integration

LocalGenius can be added as an MCP server to Claude Desktop:

```bash
# Run the installation script
./install.sh

# This will:
# 1. Install dependencies
# 2. Create run-mcp-server.sh
# 3. Show you the Claude Desktop config
```

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "localgenius": {
      "command": "/path/to/localgenius/run-mcp-server.sh",
      "args": [],
      "env": {
        "OPENAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Available MCP Tools

- **search** - Semantic search through documents
  - `query`: Search query
  - `limit`: Max results (default: 5)
  - `threshold`: Similarity threshold (default: 0.7)

- **ask** - RAG-powered Q&A
  - `question`: Your question
  - `model`: GPT model (default: gpt-3.5-turbo)

- **status** - Get index statistics

### Usage in Claude

Once configured, you can:
- "Search my documents for Python examples"
- "What do my files say about authentication?"
- "Show me the LocalGenius status"

## Development Notes

- Admin web interface (`/admin-web`) not integrated yet
- PDF and DOCX support planned but not implemented
- FAISS index doesn't support deletion (requires rebuild)
- No test framework currently set up