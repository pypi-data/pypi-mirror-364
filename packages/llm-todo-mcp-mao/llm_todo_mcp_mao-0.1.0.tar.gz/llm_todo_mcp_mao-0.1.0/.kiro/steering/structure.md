# Project Structure

## Root Directory Organization
```
/
├── src/                    # Source code
│   └── todo_mcp/          # Main MCP server package
├── tests/                 # Test files
├── docs/                  # Documentation
├── data/                  # Markdown task files storage
│   ├── tasks/             # Individual task markdown files
│   └── templates/         # Task templates
├── .kiro/                 # Kiro configuration
├── pyproject.toml         # Project configuration and dependencies
├── uv.lock               # Lock file for reproducible builds
├── README.md             # Project documentation
└── .gitignore            # Git ignore rules
```

## Source Code Structure
```
src/todo_mcp/
├── __init__.py           # Package initialization
├── __main__.py           # Entry point for MCP server
├── server.py             # Main MCP server implementation
├── tools/                # MCP tool definitions
│   ├── __init__.py
│   ├── task_tools.py    # Task CRUD operations
│   ├── hierarchy_tools.py # Parent-child task management
│   ├── status_tools.py  # Task status management
│   └── query_tools.py   # Task querying and filtering
├── models/               # Data models and structures
│   ├── __init__.py
│   ├── task.py          # Task model with hierarchy support
│   ├── status.py        # Task status definitions
│   └── tool_call.py     # Tool call record model
├── storage/              # Data persistence layer
│   ├── __init__.py
│   ├── markdown_parser.py # Markdown format parser
│   ├── markdown_writer.py # Markdown format writer
│   └── file_manager.py   # File operations manager
├── services/             # Business logic and operations
│   ├── __init__.py
│   ├── task_service.py  # Core task management logic
│   └── hierarchy_service.py # Parent-child task relationships
├── utils/                # Helper functions and utilities
│   ├── __init__.py
│   ├── markdown_utils.py # Markdown processing utilities
│   ├── date_utils.py    # Date/time utilities
│   └── validators.py    # Input validation
└── config.py            # Configuration settings
```

## File Naming Conventions
- Use snake_case for all Python files: `task_service.py`, `markdown_parser.py`
- Use PascalCase for class names: `TaskService`, `AgentTool`, `MarkdownParser`
- Use snake_case for functions and variables: `create_task`, `parse_hierarchy`
- Use UPPER_CASE for constants: `TASK_STATUS`, `DEFAULT_TEMPLATE`

## MCP Tool Interface
- All MCP tools defined in `tools/` directory, organized by functionality
- Each tool follows MCP protocol specifications
- Tools should have comprehensive JSON schemas for parameters
- Tool functions return structured responses compatible with MCP format
- Support for both synchronous operations (most tools are sync)

## Markdown File Structure
- Each task stored as individual `.md` file in `data/tasks/`
- File naming: `{task_id}_{slug}.md` (e.g., `001_setup-database.md`)
- Hierarchical tasks reference parent/child relationships in YAML frontmatter
- Tool call records embedded as structured metadata

## Module Organization
- MCP server implementation in `server.py`
- Tools organized by functionality in separate modules
- Storage layer abstracts Markdown format details
- Services handle complex business logic
- Models define clear data structures with type hints

## Folder Guidelines
- `tools/` - MCP tool implementations organized by category
- `storage/` - All file I/O and Markdown format handling
- `services/` - Business logic and complex operations
- `models/` - Data structures and type definitions
- Clear separation between MCP protocol and business logic

## Import Patterns
- Use absolute imports: `from todo_mcp.models import Task`
- Group imports: standard library, third-party, local modules
- MCP tools should import minimal dependencies for performance
- Use `from module import specific_item` for clarity

## Testing Structure
```
tests/
├── __init__.py
├── test_tools/          # MCP tool tests
├── test_models/         # Model tests
├── test_storage/        # Storage layer tests
├── test_services/       # Service layer tests
├── test_server/         # MCP server tests
├── fixtures/           # Test markdown files and data
├── conftest.py         # Pytest configuration
└── test_data/          # Sample task files for testing
```

## MCP Integration Guidelines
- Tools should be stateless and idempotent when possible
- Each tool should validate inputs using JSON schemas
- Provide clear error messages that LLM agents can understand
- Tools should be atomic operations that can be composed
- Maintain comprehensive logging for debugging
- Follow MCP protocol specifications strictly
- Support for tool discovery and introspection