"""
MCP tool definitions for the Todo MCP system.

This module contains all the MCP-compatible tools that agents can use
to interact with the task management system.
"""

from .task_tools import (
    create_task,
    update_task,
    delete_task,
    get_task,
    list_tasks,
    get_task_context,
)
from .hierarchy_tools import (
    add_child_task,
    remove_child_task,
    get_task_hierarchy,
    move_task,
)
from .status_tools import (
    update_task_status,
    bulk_status_update,
    get_task_status,
    get_pending_tasks,
    get_in_progress_tasks,
    get_blocked_tasks,
    get_completed_tasks,
)
from .query_tools import (
    search_tasks,
    filter_tasks,
    get_task_statistics,
)

__all__ = [
    # Task management tools
    "create_task",
    "update_task", 
    "delete_task",
    "get_task",
    "list_tasks",
    "get_task_context",
    # Hierarchy management tools
    "add_child_task",
    "remove_child_task",
    "get_task_hierarchy",
    "move_task",
    # Status management tools
    "update_task_status",
    "bulk_status_update",
    "get_task_status",
    "get_pending_tasks",
    "get_in_progress_tasks",
    "get_blocked_tasks",
    "get_completed_tasks",
    # Query tools
    "search_tasks",
    "filter_tasks",
    "get_task_statistics",
]