"""
Main MCP server implementation for the Todo MCP system.

This module contains the core MCP server that handles tool registration,
request processing, and communication with AI agents following the
Model Context Protocol (MCP) specification.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
)

from .config import TodoConfig
from .services.task_service import TaskService


class TodoMCPServer:
    """
    Main MCP server for the Todo system.
    
    This server provides MCP-compatible tools for AI agents to manage
    tasks through structured interfaces following the MCP protocol.
    """
    
    def __init__(self, config: TodoConfig):
        """
        Initialize the Todo MCP server.
        
        Args:
            config: Configuration settings for the server
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.task_service = TaskService(config)
        
        # Initialize MCP server
        self.server = Server(self.config.server_name)
        self._setup_handlers()
        
    def _setup_handlers(self) -> None:
        """Set up MCP protocol handlers with logging and debugging support."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Handle list_tools request with logging."""
            self.logger.debug("Handling list_tools request")
            tools = self._get_tool_definitions()
            self.logger.info(f"Returning {len(tools)} available tools")
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle call_tool request with comprehensive logging."""
            self.logger.debug(f"Received call_tool request: {name}")
            return await self._handle_tool_call(name, arguments)
    
    def _get_tool_definitions(self) -> List[Tool]:
        """Get all tool definitions for MCP introspection."""
        tools = []
        
        # Task management tools
        tools.extend([
            Tool(
                name="create_task",
                description="Create a new task with optional hierarchy and metadata",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Task title"},
                        "description": {"type": "string", "description": "Task description"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "default": "medium"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Task tags"},
                        "parent_id": {"type": "string", "description": "Parent task ID"},
                        "due_date": {"type": "string", "format": "date-time", "description": "Due date in ISO format"},
                        "metadata": {"type": "object", "description": "Additional metadata"}
                    },
                    "required": ["title"]
                }
            ),
            Tool(
                name="update_task",
                description="Update an existing task's properties",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to update"},
                        "title": {"type": "string", "description": "New task title"},
                        "description": {"type": "string", "description": "New task description"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "due_date": {"type": "string", "format": "date-time"},
                        "metadata": {"type": "object"}
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="delete_task",
                description="Delete a task and handle child task relationships",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to delete"},
                        "cascade": {"type": "boolean", "default": False, "description": "Delete child tasks as well"}
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="get_task",
                description="Retrieve a single task by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to retrieve"}
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="list_tasks",
                description="List tasks with optional filtering",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "array", "items": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked"]}},
                        "priority": {"type": "array", "items": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "parent_id": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 100}
                    }
                }
            )
        ])
        
        # Status management tools
        tools.extend([
            Tool(
                name="update_task_status",
                description="Update task status with validation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to update"},
                        "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked"], "description": "New status"}
                    },
                    "required": ["task_id", "status"]
                }
            ),
            Tool(
                name="bulk_status_update",
                description="Update status for multiple tasks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_ids": {"type": "array", "items": {"type": "string"}, "description": "List of task IDs"},
                        "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked"], "description": "New status"}
                    },
                    "required": ["task_ids", "status"]
                }
            ),
            Tool(
                name="get_task_status",
                description="Get current status of a task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to check"}
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="get_pending_tasks",
                description="Get all tasks with pending status",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="get_in_progress_tasks",
                description="Get all tasks with in_progress status",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="get_blocked_tasks",
                description="Get all tasks with blocked status",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="get_completed_tasks",
                description="Get all tasks with completed status",
                inputSchema={"type": "object", "properties": {}}
            )
        ])
        
        # Hierarchy management tools
        tools.extend([
            Tool(
                name="add_child_task",
                description="Add a child task relationship",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "parent_id": {"type": "string", "description": "Parent task ID"},
                        "child_id": {"type": "string", "description": "Child task ID"}
                    },
                    "required": ["parent_id", "child_id"]
                }
            ),
            Tool(
                name="remove_child_task",
                description="Remove a child task relationship",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "parent_id": {"type": "string", "description": "Parent task ID"},
                        "child_id": {"type": "string", "description": "Child task ID"}
                    },
                    "required": ["parent_id", "child_id"]
                }
            ),
            Tool(
                name="get_task_hierarchy",
                description="Get task hierarchy tree",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "root_id": {"type": "string", "description": "Root task ID (optional)"}
                    }
                }
            ),
            Tool(
                name="move_task",
                description="Move a task to a different parent",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to move"},
                        "new_parent_id": {"type": "string", "description": "New parent task ID (null for root level)"}
                    },
                    "required": ["task_id"]
                }
            )
        ])
        
        # Query tools
        tools.extend([
            Tool(
                name="search_tasks",
                description="Search tasks by text content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="filter_tasks",
                description="Filter tasks with advanced criteria",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "array", "items": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked"]}},
                        "priority": {"type": "array", "items": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "created_after": {"type": "string", "format": "date-time"},
                        "created_before": {"type": "string", "format": "date-time"},
                        "due_after": {"type": "string", "format": "date-time"},
                        "due_before": {"type": "string", "format": "date-time"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 100}
                    }
                }
            ),
            Tool(
                name="get_task_statistics",
                description="Get task statistics and metrics",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="get_task_context",
                description="Get complete context for a task including hierarchy and history",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to get context for"}
                    },
                    "required": ["task_id"]
                }
            )
        ])
        
        return tools
    
    async def _handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Handle a tool call from an AI agent with unified error handling and logging.
        
        Args:
            name: Name of the tool to call
            arguments: Arguments for the tool call
            
        Returns:
            Tool call result as TextContent with proper formatting
        """
        # Log the incoming request
        self.logger.info(f"Tool call: {name}")
        self.logger.debug(f"Tool call {name} with arguments: {arguments}")
        
        # Record start time for performance monitoring
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Initialize task service if needed
            if not hasattr(self.task_service, '_initialized') or not self.task_service._initialized:
                self.logger.debug("Initializing task service")
                await self.task_service.initialize()
            
            # Route to appropriate handler
            handler_map = {
                "create_task": self._handle_create_task,
                "update_task": self._handle_update_task,
                "delete_task": self._handle_delete_task,
                "get_task": self._handle_get_task,
                "list_tasks": self._handle_list_tasks,
                "update_task_status": self._handle_update_task_status,
                "bulk_status_update": self._handle_bulk_status_update,
                "get_task_status": self._handle_get_task_status,
                "get_pending_tasks": self._handle_get_pending_tasks,
                "get_in_progress_tasks": self._handle_get_in_progress_tasks,
                "get_blocked_tasks": self._handle_get_blocked_tasks,
                "get_completed_tasks": self._handle_get_completed_tasks,
                "add_child_task": self._handle_add_child_task,
                "remove_child_task": self._handle_remove_child_task,
                "get_task_hierarchy": self._handle_get_task_hierarchy,
                "move_task": self._handle_move_task,
                "search_tasks": self._handle_search_tasks,
                "filter_tasks": self._handle_filter_tasks,
                "get_task_statistics": self._handle_get_task_statistics,
                "get_task_context": self._handle_get_task_context,
            }
            
            handler = handler_map.get(name)
            if not handler:
                raise ValueError(f"Unknown tool: {name}")
            
            # Execute the tool handler
            result = await handler(arguments)
            
            # Calculate execution time
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Log successful completion
            self.logger.info(f"Tool call {name} completed successfully in {execution_time:.3f}s")
            self.logger.debug(f"Tool call {name} result: {result}")
            
            # Format response
            formatted_result = self._format_tool_response(result, name)
            return [TextContent(type="text", text=formatted_result)]
            
        except Exception as e:
            # Calculate execution time for failed requests
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Log error with context
            self.logger.error(f"Tool call {name} failed after {execution_time:.3f}s: {e}")
            self.logger.debug(f"Tool call {name} error details", exc_info=True)
            
            # Format error response
            error_response = self._format_error_response(e, name, arguments)
            return [TextContent(type="text", text=error_response)]
    
    def _format_tool_response(self, result: Any, tool_name: str) -> str:
        """
        Format tool response for consistent output.
        
        Args:
            result: Tool execution result
            tool_name: Name of the tool that was executed
            
        Returns:
            Formatted response string
        """
        import json
        
        try:
            # If result is already a string, return as-is
            if isinstance(result, str):
                return result
            
            # If result is a dict or list, format as JSON
            if isinstance(result, (dict, list)):
                return json.dumps(result, indent=2, ensure_ascii=False)
            
            # For other types, convert to string
            return str(result)
            
        except Exception as e:
            self.logger.warning(f"Failed to format response for {tool_name}: {e}")
            return str(result)
    
    def _format_error_response(self, error: Exception, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Format error response with helpful information for agents.
        
        Args:
            error: The exception that occurred
            tool_name: Name of the tool that failed
            arguments: Arguments that were passed to the tool
            
        Returns:
            Formatted error message
        """
        import json
        
        # Determine error type and create appropriate response
        error_type = type(error).__name__
        error_message = str(error)
        
        # Create structured error response
        error_response = {
            "error": True,
            "error_type": error_type,
            "message": error_message,
            "tool": tool_name,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Add suggestions based on error type
        if "not found" in error_message.lower():
            error_response["suggestion"] = "Check if the task ID exists using list_tasks or get_task"
        elif "validation" in error_message.lower():
            error_response["suggestion"] = "Check the input parameters match the expected schema"
        elif "permission" in error_message.lower():
            error_response["suggestion"] = "Verify you have the necessary permissions for this operation"
        
        try:
            return json.dumps(error_response, indent=2, ensure_ascii=False)
        except Exception:
            # Fallback to simple error message
            return f"Error executing {tool_name}: {error_message}"
    
    # Tool handler methods
    async def _handle_create_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_task tool call."""
        from .tools.task_tools import create_task
        return await create_task(arguments)
    
    async def _handle_update_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_task tool call."""
        from .tools.task_tools import update_task
        return await update_task(arguments)
    
    async def _handle_delete_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delete_task tool call."""
        from .tools.task_tools import delete_task
        return await delete_task(arguments)
    
    async def _handle_get_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_task tool call."""
        from .tools.task_tools import get_task
        return await get_task(arguments)
    
    async def _handle_list_tasks(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_tasks tool call."""
        from .tools.task_tools import list_tasks
        return await list_tasks(arguments)
    
    async def _handle_update_task_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_task_status tool call."""
        from .tools.status_tools import update_task_status
        return await update_task_status(arguments)
    
    async def _handle_get_pending_tasks(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_pending_tasks tool call."""
        from .tools.status_tools import get_pending_tasks
        return await get_pending_tasks(arguments)
    
    async def _handle_get_in_progress_tasks(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_in_progress_tasks tool call."""
        from .tools.status_tools import get_in_progress_tasks
        return await get_in_progress_tasks(arguments)
    
    async def _handle_get_blocked_tasks(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_blocked_tasks tool call."""
        from .tools.status_tools import get_blocked_tasks
        return await get_blocked_tasks(arguments)
    
    async def _handle_get_completed_tasks(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_completed_tasks tool call."""
        from .tools.status_tools import get_completed_tasks
        return await get_completed_tasks(arguments)
    
    async def _handle_bulk_status_update(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle bulk_status_update tool call."""
        from .tools.status_tools import bulk_status_update
        return await bulk_status_update(arguments)
    
    async def _handle_get_task_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_task_status tool call."""
        from .tools.status_tools import get_task_status
        return await get_task_status(arguments)
    
    async def _handle_add_child_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add_child_task tool call."""
        from .tools.hierarchy_tools import add_child_task
        return await add_child_task(arguments)
    
    async def _handle_remove_child_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle remove_child_task tool call."""
        from .tools.hierarchy_tools import remove_child_task
        return await remove_child_task(arguments)
    
    async def _handle_get_task_hierarchy(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_task_hierarchy tool call."""
        from .tools.hierarchy_tools import get_task_hierarchy
        return await get_task_hierarchy(arguments)
    
    async def _handle_move_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle move_task tool call."""
        from .tools.hierarchy_tools import move_task
        return await move_task(arguments)
    
    async def _handle_search_tasks(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search_tasks tool call."""
        from .tools.query_tools import search_tasks
        return await search_tasks(arguments)
    
    async def _handle_filter_tasks(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle filter_tasks tool call."""
        from .tools.query_tools import filter_tasks
        return await filter_tasks(arguments)
    
    async def _handle_get_task_statistics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_task_statistics tool call."""
        from .tools.query_tools import get_task_statistics
        return await get_task_statistics(arguments)
    
    async def _handle_get_task_context(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_task_context tool call."""
        from .tools.task_tools import get_task_context
        return await get_task_context(arguments)
    
    async def run(self) -> None:
        """
        Run the MCP server.
        
        This method starts the server and handles incoming requests
        from AI agents through the MCP protocol.
        """
        self.logger.info(f"Starting {self.config.server_name} v{self.config.server_version}")
        
        try:
            # Initialize task service
            await self.task_service.initialize()
            
            # Run the MCP server with stdio transport
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.config.server_name,
                    self.config.server_version
                )
                
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            raise
        finally:
            # Cleanup
            await self.task_service.cleanup()
            self.logger.info("Server shutdown complete")
    
    async def shutdown(self) -> None:
        """
        Gracefully shutdown the MCP server.
        
        This method performs cleanup operations and ensures
        all resources are properly released.
        """
        self.logger.info("Initiating server shutdown...")
        
        try:
            # Cleanup task service
            if hasattr(self.task_service, 'cleanup'):
                await self.task_service.cleanup()
            
            self.logger.info("Server shutdown completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during server shutdown: {e}")
            raise