"""
Helper functions and utilities for the Todo MCP system.

This module contains utility functions for markdown processing,
date/time operations, validation, and other common operations.
"""

from .markdown_utils import (
    slugify,
    format_task_content,
    parse_yaml_frontmatter,
)
from .date_utils import (
    parse_datetime,
    format_datetime,
    is_valid_date,
)
from .validators import (
    validate_task_id,
    validate_task_title,
    validate_priority,
    validate_status,
)
from .cache import (
    LRUCache,
    TaskCache,
    CacheManager,
    get_cache_manager,
    initialize_cache,
)
from .indexing import (
    HashIndex,
    RangeIndex,
    TextIndex,
    TaskIndexManager,
    QueryOptimizer,
    QueryResult,
    PaginatedResult,
    get_index_manager,
    initialize_indexing,
)

__all__ = [
    # Markdown utilities
    "slugify",
    "format_task_content",
    "parse_yaml_frontmatter",
    # Date utilities
    "parse_datetime",
    "format_datetime", 
    "is_valid_date",
    # Validators
    "validate_task_id",
    "validate_task_title",
    "validate_priority",
    "validate_status",
    # Cache utilities
    "LRUCache",
    "TaskCache",
    "CacheManager",
    "get_cache_manager",
    "initialize_cache",
    # Indexing utilities
    "HashIndex",
    "RangeIndex",
    "TextIndex",
    "TaskIndexManager",
    "QueryOptimizer",
    "QueryResult",
    "PaginatedResult",
    "get_index_manager",
    "initialize_indexing",
]