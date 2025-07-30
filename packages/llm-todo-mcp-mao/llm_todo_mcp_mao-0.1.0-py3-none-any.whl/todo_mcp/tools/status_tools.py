"""
MCP tools for task status management.

This module provides MCP-compatible tools for managing task statuses
and retrieving tasks by status with Pydantic validation.
"""

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError

from ..config import TodoConfig
from ..models.task import Task
from ..models.status import TaskStatus, Priority, validate_status_transition, StatusTransitionError
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

class UpdateTaskStatusRequest(BaseModel):
    """Request model for updating task status."""
    task_id: str = Field(..., description="Task identifier")
    status: str = Field(..., description="New status (pending, in_progress, completed, blocked)")


class BulkStatusUpdateRequest(BaseModel):
    """Request model for bulk status update."""
    task_ids: List[str] = Field(..., min_length=1, description="List of task identifiers")
    status: str = Field(..., description="New status for all tasks")


class GetTaskStatusRequest(BaseModel):
    """Request model for getting task status."""
    task_id: str = Field(..., description="Task identifier")


class TaskStatusResponse(BaseModel):
    """Response model for task status information."""
    task_id: str
    current_status: str
    valid_transitions: List[str]
    status_description: str


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
    status_filter: str


class BulkUpdateResult(BaseModel):
    """Response model for bulk update results."""
    successful_updates: List[str]
    failed_updates: List[Dict[str, str]]
    total_processed: int
    success_count: int
    failure_count: int


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


def _parse_status(status_str: str) -> TaskStatus:
    """Parse status string to TaskStatus enum."""
    try:
        return TaskStatus.from_string(status_str)
    except ValueError:
        raise ValueError(f"Invalid status: {status_str}. Must be one of: pending, in_progress, completed, blocked")


async def update_task_status(task_id: str, status: str) -> Dict[str, Any]:
    """
    Update the status of a task.
    
    Args:
        task_id: Task identifier
        status: New status (pending, in_progress, completed, blocked)
        
    Returns:
        Operation result
    """
    try:
        # Validate input using Pydantic
        request = UpdateTaskStatusRequest(task_id=task_id, status=status)
        
        # Parse status
        new_status = _parse_status(request.status)
        
        # Get task service
        service = await _get_task_service()
        
        # Get current task to validate transition
        current_task = await service.get_task(request.task_id)
        if not current_task:
            return ToolResponse(
                success=False,
                error=f"Task not found: {request.task_id}"
            ).model_dump()
        
        # Validate status transition
        try:
            validate_status_transition(current_task.status, new_status)
        except StatusTransitionError as e:
            return ToolResponse(
                success=False,
                error=str(e)
            ).model_dump()
        
        # Update task status
        updated_task = await service.update_task(request.task_id, status=new_status)
        
        if not updated_task:
            return ToolResponse(
                success=False,
                error=f"Failed to update task status: {request.task_id}"
            ).model_dump()
        
        # Return response
        response = ToolResponse(
            success=True,
            data=_task_to_response(updated_task),
            message=f"Task status updated to '{new_status.value}': {request.task_id}"
        )
        
        logger.info(f"Updated task status: {request.task_id} -> {new_status.value}")
        return response.model_dump()
        
    except (ValidationError, ValueError) as e:
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
        error_msg = f"Unexpected error updating task status: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def bulk_status_update(task_ids: List[str], status: str) -> Dict[str, Any]:
    """
    Update status for multiple tasks.
    
    Args:
        task_ids: List of task identifiers
        status: New status for all tasks
        
    Returns:
        Operation result
    """
    try:
        # Validate input using Pydantic
        request = BulkStatusUpdateRequest(task_ids=task_ids, status=status)
        
        # Parse status
        new_status = _parse_status(request.status)
        
        # Get task service
        service = await _get_task_service()
        
        # Process each task
        successful_updates = []
        failed_updates = []
        
        for task_id in request.task_ids:
            try:
                # Get current task
                current_task = await service.get_task(task_id)
                if not current_task:
                    failed_updates.append({
                        "task_id": task_id,
                        "error": "Task not found"
                    })
                    continue
                
                # Validate status transition
                try:
                    validate_status_transition(current_task.status, new_status)
                except StatusTransitionError as e:
                    failed_updates.append({
                        "task_id": task_id,
                        "error": str(e)
                    })
                    continue
                
                # Update task status
                updated_task = await service.update_task(task_id, status=new_status)
                
                if updated_task:
                    successful_updates.append(task_id)
                else:
                    failed_updates.append({
                        "task_id": task_id,
                        "error": "Failed to update task"
                    })
                    
            except Exception as e:
                failed_updates.append({
                    "task_id": task_id,
                    "error": str(e)
                })
        
        # Create result
        result = BulkUpdateResult(
            successful_updates=successful_updates,
            failed_updates=failed_updates,
            total_processed=len(request.task_ids),
            success_count=len(successful_updates),
            failure_count=len(failed_updates)
        )
        
        # Return response
        response = ToolResponse(
            success=True,
            data=result.model_dump(),
            message=f"Bulk update completed: {result.success_count} successful, {result.failure_count} failed"
        )
        
        logger.info(f"Bulk status update: {result.success_count}/{result.total_processed} successful")
        return response.model_dump()
        
    except (ValidationError, ValueError) as e:
        error_msg = f"Validation error: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()
    
    except Exception as e:
        error_msg = f"Unexpected error in bulk status update: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get current status of a task.
    
    Args:
        task_id: Task identifier
        
    Returns:
        Task status information
    """
    try:
        # Validate input using Pydantic
        request = GetTaskStatusRequest(task_id=task_id)
        
        # Get task service
        service = await _get_task_service()
        
        # Get task
        task = await service.get_task(request.task_id)
        
        if not task:
            return ToolResponse(
                success=False,
                error=f"Task not found: {request.task_id}"
            ).model_dump()
        
        # Get valid transitions
        from ..models.status import get_valid_transitions, get_status_description
        valid_transitions = get_valid_transitions(task.status)
        
        # Create status response
        status_info = TaskStatusResponse(
            task_id=task.id,
            current_status=task.status.value,
            valid_transitions=[s.value for s in valid_transitions],
            status_description=get_status_description(task.status)
        )
        
        # Return response
        response = ToolResponse(
            success=True,
            data=status_info.model_dump()
        )
        
        return response.model_dump()
        
    except ValidationError as e:
        error_msg = f"Validation error: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()
    
    except Exception as e:
        error_msg = f"Unexpected error getting task status: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def get_pending_tasks() -> Dict[str, Any]:
    """
    Get all pending tasks.
    
    Returns:
        List of pending tasks
    """
    try:
        # Get task service
        service = await _get_task_service()
        
        # Get pending tasks
        tasks = await service.get_tasks_by_status(TaskStatus.PENDING)
        
        # Convert to response format
        task_responses = [_task_to_response(task) for task in tasks]
        
        list_response = TaskListResponse(
            tasks=task_responses,
            total_count=len(task_responses),
            status_filter="pending"
        )
        
        # Return response
        response = ToolResponse(
            success=True,
            data=list_response.model_dump(),
            message=f"Found {len(task_responses)} pending tasks"
        )
        
        return response.model_dump()
        
    except Exception as e:
        error_msg = f"Unexpected error getting pending tasks: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def get_in_progress_tasks() -> Dict[str, Any]:
    """
    Get all in-progress tasks.
    
    Returns:
        List of in-progress tasks
    """
    try:
        # Get task service
        service = await _get_task_service()
        
        # Get in-progress tasks
        tasks = await service.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        
        # Convert to response format
        task_responses = [_task_to_response(task) for task in tasks]
        
        list_response = TaskListResponse(
            tasks=task_responses,
            total_count=len(task_responses),
            status_filter="in_progress"
        )
        
        # Return response
        response = ToolResponse(
            success=True,
            data=list_response.model_dump(),
            message=f"Found {len(task_responses)} in-progress tasks"
        )
        
        return response.model_dump()
        
    except Exception as e:
        error_msg = f"Unexpected error getting in-progress tasks: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def get_blocked_tasks() -> Dict[str, Any]:
    """
    Get all blocked tasks.
    
    Returns:
        List of blocked tasks
    """
    try:
        # Get task service
        service = await _get_task_service()
        
        # Get blocked tasks
        tasks = await service.get_tasks_by_status(TaskStatus.BLOCKED)
        
        # Convert to response format
        task_responses = [_task_to_response(task) for task in tasks]
        
        list_response = TaskListResponse(
            tasks=task_responses,
            total_count=len(task_responses),
            status_filter="blocked"
        )
        
        # Return response
        response = ToolResponse(
            success=True,
            data=list_response.model_dump(),
            message=f"Found {len(task_responses)} blocked tasks"
        )
        
        return response.model_dump()
        
    except Exception as e:
        error_msg = f"Unexpected error getting blocked tasks: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def get_completed_tasks() -> Dict[str, Any]:
    """
    Get all completed tasks.
    
    Returns:
        List of completed tasks
    """
    try:
        # Get task service
        service = await _get_task_service()
        
        # Get completed tasks
        tasks = await service.get_tasks_by_status(TaskStatus.COMPLETED)
        
        # Convert to response format
        task_responses = [_task_to_response(task) for task in tasks]
        
        list_response = TaskListResponse(
            tasks=task_responses,
            total_count=len(task_responses),
            status_filter="completed"
        )
        
        # Return response
        response = ToolResponse(
            success=True,
            data=list_response.model_dump(),
            message=f"Found {len(task_responses)} completed tasks"
        )
        
        return response.model_dump()
        
    except Exception as e:
        error_msg = f"Unexpected error getting completed tasks: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()