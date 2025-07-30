"""
Todo MCP Server - A task management system designed for AI agents.

This package provides a Model Context Protocol (MCP) server that enables
AI agents to manage tasks through structured tools and interfaces.
"""

__version__ = "0.1.0"
__author__ = "Todo MCP Team"
__email__ = "team@todo-mcp.dev"

from .models.task import Task, TaskStatus, Priority
from .models.tool_call import ToolCall

__all__ = [
    "Task",
    "TaskStatus", 
    "Priority",
    "ToolCall",
]