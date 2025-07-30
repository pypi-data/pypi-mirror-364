# Technology Stack

## Core Technology
- Python 3.8+ as the primary programming language
- Pure Python implementation for simplicity and portability

## Package Management
- uv for fast Python package management and virtual environments
- pyproject.toml for project configuration and dependencies

## MCP Server Integration
- Model Context Protocol (MCP) server implementation
- JSON-RPC 2.0 protocol for communication
- Tool discovery and introspection capabilities
- Structured JSON schemas for all tool parameters
- Standard input/output for MCP communication

## User Interface
- Rich library for terminal-based UI components
- Click for command-line interface
- Colorama for cross-platform colored terminal output
- Interactive mode for agent collaboration

## Data Storage
- Markdown files as primary storage format (human and LLM readable)
- YAML frontmatter for task metadata
- File-based storage for scalability and version control
- JSON for configuration and temporary data

## Development Tools
- Package manager: uv
- MCP SDK: mcp library for Python
- Code formatting: black
- Import sorting: isort
- Linting: ruff (fast Python linter)
- Type checking: mypy
- JSON schema validation: jsonschema

## Common Commands
```bash
# Create virtual environment and install dependencies
uv sync

# Run the MCP server
uv run python -m todo_mcp

# Run with specific script
uv run todo-mcp-server

# Test MCP server locally
uv run todo-mcp-server --test

# Install new dependency
uv add <package-name>

# Install development dependency
uv add --dev <package-name>

# Run tests
uv run pytest

# Run MCP tool tests specifically
uv run pytest tests/test_tools/

# Format code
uv run black .

# Sort imports
uv run isort .

# Lint code
uv run ruff check .

# Type check
uv run mypy .

# Validate markdown task files
uv run todo-mcp-server validate

# Test MCP tool schemas
uv run todo-mcp-server test-schemas
```

## Code Quality
- Use type hints for better code documentation and IDE support
- Write unit tests with pytest
- Follow PEP 8 style guidelines
- Keep functions small and focused
- Use descriptive variable and function names