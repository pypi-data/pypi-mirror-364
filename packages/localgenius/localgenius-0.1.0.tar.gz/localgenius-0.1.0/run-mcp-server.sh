#!/bin/bash
# MCP Server launcher for LocalGenius

# Set up environment
export PYTHONPATH="/Users/marcokotrotsos/projects/localgenius:$PYTHONPATH"

# Use the Python from your conda installation
PYTHON="/opt/homebrew/Caskroom/miniconda/base/bin/python3"

# Check if localgenius environment exists and use it
if [ -f "/opt/homebrew/Caskroom/miniconda/base/envs/localgenius/bin/python" ]; then
    PYTHON="/opt/homebrew/Caskroom/miniconda/base/envs/localgenius/bin/python"
fi

# Run the FastMCP server
exec "$PYTHON" /Users/marcokotrotsos/projects/localgenius/localgenius/mcp/fastmcp_server.py