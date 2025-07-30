"""
MCP tools for basic task management operations.

This module provides MCP-compatible tools for creating, reading,
updating, and deleting tasks with Pydantic validation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError

from ..config import TodoConfig
from ..models.task import Task
from ..models.status import TaskStatus, Priority
from ..services.task_service import TaskService, TaskServiceError, TaskNotFoundError, TaskValidationError


# Global service instance
_task_service: Optional[TaskService] = None
_config: Optional[TodoConfig] = None

logger = logging.getLogger(__name__)


async def _get_task_service() -> TaskService:
    """Get or initialize the task service."""
    global _task_service, _config
    
    if _task_service is None:
        from ..config import config
        _config = config
        _task_service = TaskService(_config)
        await _task_service.initialize()
    
    return _task_service


# Pydantic models for tool parameters and responses

class CreateTaskRequest(BaseModel):
    """Request model for creating a task."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str = Field(default="", description="Task description")
    priority: str = Field(default="medium", description="Task priority (low, medium, high, urgent)")
    tags: Optional[List[str]] = Field(default=None, description="List of task tags")
    parent_id: Optional[str] = Field(default=None, description="Parent task ID for hierarchy")
    due_date: Optional[str] = Field(default=None, description="Due date in ISO format")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional task metadata")


class UpdateTaskRequest(BaseModel):
    """Request model for updating a task."""
    task_id: str = Field(..., description="Task identifier")
    title: Optional[str] = Field(default=None, min_length=1, max_length=200, description="New task title")
    description: Optional[str] = Field(default=None, description="New task description")
    priority: Optional[str] = Field(default=None, description="New task priority")
    tags: Optional[List[str]] = Field(default=None, description="New list of tags")
    due_date: Optional[str] = Field(default=None, description="New due date in ISO format")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="New task metadata")


class DeleteTaskRequest(BaseModel):
    """Request model for deleting a task."""
    task_id: str = Field(..., description="Task identifier")
    cascade: bool = Field(default=False, description="Delete child tasks as well")


class GetTaskRequest(BaseModel):
    """Request model for getting a task."""
    task_id: str = Field(..., description="Task identifier")


class ListTasksRequest(BaseModel):
    """Request model for listing tasks."""
    status: Optional[str] = Field(default=None, description="Filter by status")
    priority: Optional[str] = Field(default=None, description="Filter by priority")
    tags: Optional[List[str]] = Field(default=None, description="Filter by tags")
    parent_id: Optional[str] = Field(default=None, description="Filter by parent task ID")
    include_completed: bool = Field(default=True, description="Include completed tasks")


class TaskResponse(BaseModel):
    """Response model for task data."""
    id: str
    title: str
    description: str
    status: str
    priority: str
    tags: List[str]
    parent_id: Optional[str]
    child_ids: List[str]
    created_at: str
    updated_at: str
    due_date: Optional[str]
    metadata: Dict[str, Any]


class TaskListResponse(BaseModel):
    """Response model for task list."""
    tasks: List[TaskResponse]
    total_count: int


class ToolResponse(BaseModel):
    """Standard tool response format."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


def _task_to_response(task: Task) -> TaskResponse:
    """Convert Task model to TaskResponse."""
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status.value,
        priority=task.priority.name.lower(),
        tags=task.tags,
        parent_id=task.parent_id,
        child_ids=task.child_ids,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
        due_date=task.due_date.isoformat() if task.due_date else None,
        metadata=task.metadata
    )


def _parse_priority(priority_str: str) -> Priority:
    """Parse priority string to Priority enum."""
    try:
        return Priority.from_string(priority_str)
    except ValueError:
        raise ValidationError(f"Invalid priority: {priority_str}. Must be one of: low, medium, high, urgent")


def _parse_status(status_str: str) -> TaskStatus:
    """Parse status string to TaskStatus enum."""
    try:
        return TaskStatus.from_string(status_str)
    except ValueError:
        raise ValidationError(f"Invalid status: {status_str}. Must be one of: pending, in_progress, completed, blocked")


def _parse_datetime(date_str: str) -> datetime:
    """Parse ISO datetime string."""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        raise ValidationError(f"Invalid datetime format: {date_str}. Use ISO format (e.g., 2024-01-20T17:00:00Z)")


async def create_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    tags: Optional[List[str]] = None,
    parent_id: Optional[str] = None,
    due_date: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a new task.
    
    Args:
        title: Task title
        description: Task description
        priority: Task priority (low, medium, high, urgent)
        tags: List of tags
        parent_id: Parent task ID for hierarchy
        due_date: Due date in ISO format
        metadata: Additional task metadata
        
    Returns:
        Created task data
    """
    try:
        # Validate input using Pydantic
        request = CreateTaskRequest(
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            parent_id=parent_id,
            due_date=due_date,
            metadata=metadata
        )
        
        # Parse priority and due date
        priority_enum = _parse_priority(request.priority)
        due_date_parsed = _parse_datetime(request.due_date) if request.due_date else None
        
        # Get task service
        service = await _get_task_service()
        
        # Create task
        task = await service.create_task(
            title=request.title,
            description=request.description,
            priority=priority_enum,
            tags=request.tags or [],
            parent_id=request.parent_id,
            due_date=due_date_parsed,
            metadata=request.metadata or {}
        )
        
        # Return response
        response = ToolResponse(
            success=True,
            data=_task_to_response(task),
            message=f"Task created successfully: {task.id}"
        )
        
        logger.info(f"Created task: {task.id} - {task.title}")
        return response.model_dump()
        
    except ValidationError as e:
        error_msg = f"Validation error: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()
    
    except TaskValidationError as e:
        error_msg = f"Task validation error: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()
    
    except TaskServiceError as e:
        error_msg = f"Task service error: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()
    
    except Exception as e:
        error_msg = f"Unexpected error creating task: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Update an existing task.
    
    Args:
        task_id: Task identifier
        title: New task title
        description: New task description
        priority: New task priority
        tags: New list of tags
        due_date: New due date in ISO format
        metadata: New task metadata
        
    Returns:
        Updated task data
    """
    try:
        # Validate input using Pydantic
        request = UpdateTaskRequest(
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            due_date=due_date,
            metadata=metadata
        )
        
        # Get task service
        service = await _get_task_service()
        
        # Prepare updates
        updates = {}
        
        if request.title is not None:
            updates['title'] = request.title
        
        if request.description is not None:
            updates['description'] = request.description
        
        if request.priority is not None:
            updates['priority'] = _parse_priority(request.priority)
        
        if request.tags is not None:
            updates['tags'] = request.tags
        
        if request.due_date is not None:
            updates['due_date'] = _parse_datetime(request.due_date)
        
        if request.metadata is not None:
            updates['metadata'] = request.metadata
        
        # Update task
        task = await service.update_task(request.task_id, **updates)
        
        if not task:
            return ToolResponse(
                success=False,
                error=f"Task not found: {request.task_id}"
            ).model_dump()
        
        # Return response
        response = ToolResponse(
            success=True,
            data=_task_to_response(task),
            message=f"Task updated successfully: {task.id}"
        )
        
        logger.info(f"Updated task: {task.id}")
        return response.model_dump()
        
    except ValidationError as e:
        error_msg = f"Validation error: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()
    
    except TaskValidationError as e:
        error_msg = f"Task validation error: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()
    
    except TaskServiceError as e:
        error_msg = f"Task service error: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()
    
    except Exception as e:
        error_msg = f"Unexpected error updating task: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def delete_task(task_id: str, cascade: bool = False) -> Dict[str, Any]:
    """
    Delete a task.
    
    Args:
        task_id: Task identifier
        cascade: Delete child tasks as well
        
    Returns:
        Deletion result
    """
    try:
        # Validate input using Pydantic
        request = DeleteTaskRequest(task_id=task_id, cascade=cascade)
        
        # Get task service
        service = await _get_task_service()
        
        # Delete task
        deleted = await service.delete_task(request.task_id, cascade=request.cascade)
        
        if not deleted:
            return ToolResponse(
                success=False,
                error=f"Task not found: {request.task_id}"
            ).model_dump()
        
        # Return response
        response = ToolResponse(
            success=True,
            message=f"Task deleted successfully: {request.task_id}"
        )
        
        logger.info(f"Deleted task: {request.task_id}")
        return response.model_dump()
        
    except ValidationError as e:
        error_msg = f"Validation error: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()
    
    except TaskServiceError as e:
        error_msg = f"Task service error: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()
    
    except Exception as e:
        error_msg = f"Unexpected error deleting task: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def get_task(task_id: str) -> Dict[str, Any]:
    """
    Get a task by ID.
    
    Args:
        task_id: Task identifier
        
    Returns:
        Task data
    """
    try:
        # Validate input using Pydantic
        request = GetTaskRequest(task_id=task_id)
        
        # Get task service
        service = await _get_task_service()
        
        # Get task
        task = await service.get_task(request.task_id)
        
        if not task:
            return ToolResponse(
                success=False,
                error=f"Task not found: {request.task_id}"
            ).model_dump()
        
        # Return response
        response = ToolResponse(
            success=True,
            data=_task_to_response(task)
        )
        
        return response.model_dump()
        
    except ValidationError as e:
        error_msg = f"Validation error: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()
    
    except Exception as e:
        error_msg = f"Unexpected error getting task: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    parent_id: Optional[str] = None,
    include_completed: bool = True,
) -> Dict[str, Any]:
    """
    List tasks with optional filtering.
    
    Args:
        status: Filter by status
        priority: Filter by priority
        tags: Filter by tags
        parent_id: Filter by parent task ID
        include_completed: Include completed tasks
        
    Returns:
        List of tasks
    """
    try:
        # Validate input using Pydantic
        request = ListTasksRequest(
            status=status,
            priority=priority,
            tags=tags,
            parent_id=parent_id,
            include_completed=include_completed
        )
        
        # Get task service
        service = await _get_task_service()
        
        # Parse filters
        status_enum = None
        if request.status:
            status_enum = _parse_status(request.status)
        
        priority_enum = None
        if request.priority:
            priority_enum = _parse_priority(request.priority)
        
        # List tasks
        tasks = await service.list_tasks(
            status=status_enum,
            priority=priority_enum,
            tags=request.tags,
            parent_id=request.parent_id,
            include_completed=request.include_completed
        )
        
        # Convert to response format
        task_responses = [_task_to_response(task) for task in tasks]
        
        list_response = TaskListResponse(
            tasks=task_responses,
            total_count=len(task_responses)
        )
        
        # Return response
        response = ToolResponse(
            success=True,
            data=list_response.model_dump()
        )
        
        return response.model_dump()
        
    except ValidationError as e:
        error_msg = f"Validation error: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()
    
    except Exception as e:
        error_msg = f"Unexpected error listing tasks: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def get_task_context(task_id: str) -> Dict[str, Any]:
    """
    Get task with full context including hierarchy and relationships.
    
    Args:
        task_id: Task identifier
        
    Returns:
        Task with context data
    """
    try:
        # Validate input using Pydantic
        request = GetTaskRequest(task_id=task_id)
        
        # Get task service
        service = await _get_task_service()
        
        # Get main task
        task = await service.get_task(request.task_id)
        
        if not task:
            return ToolResponse(
                success=False,
                error=f"Task not found: {request.task_id}"
            ).model_dump()
        
        # Get parent task if exists
        parent_task = None
        if task.parent_id:
            parent_task = await service.get_task(task.parent_id)
        
        # Get child tasks
        child_tasks = []
        for child_id in task.child_ids:
            child_task = await service.get_task(child_id)
            if child_task:
                child_tasks.append(child_task)
        
        # Build context response
        context_data = {
            "task": _task_to_response(task).model_dump(),
            "parent": _task_to_response(parent_task).model_dump() if parent_task else None,
            "children": [_task_to_response(child).model_dump() for child in child_tasks],
            "hierarchy_depth": 0,  # TODO: Calculate actual depth
            "total_descendants": len(child_tasks)  # TODO: Calculate recursive count
        }
        
        # Return response
        response = ToolResponse(
            success=True,
            data=context_data
        )
        
        return response.model_dump()
        
    except ValidationError as e:
        error_msg = f"Validation error: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()
    
    except Exception as e:
        error_msg = f"Unexpected error getting task context: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()