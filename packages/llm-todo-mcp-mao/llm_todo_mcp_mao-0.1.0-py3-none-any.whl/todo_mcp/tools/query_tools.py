"""
MCP tools for task querying and filtering.

This module provides MCP-compatible tools for searching, filtering,
and getting statistics about tasks with Pydantic validation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError

from ..config import TodoConfig
from ..models.task import Task
from ..models.status import TaskStatus, Priority
from ..models.filters import TaskFilter, TaskSearchResult
from ..services.task_service import TaskService, TaskServiceError


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

class SearchTasksRequest(BaseModel):
    """Request model for searching tasks."""
    search_text: str = Field(..., min_length=1, max_length=200, description="Text to search for")
    search_fields: Optional[List[str]] = Field(
        default=None, 
        description="Fields to search in (title, description, tags)"
    )
    status: Optional[List[str]] = Field(default=None, description="Filter by status(es)")
    priority: Optional[List[str]] = Field(default=None, description="Filter by priority(ies)")
    tags: Optional[List[str]] = Field(default=None, description="Filter by tags")
    include_completed: bool = Field(default=True, description="Include completed tasks")
    limit: Optional[int] = Field(default=None, ge=1, le=1000, description="Maximum results")
    offset: int = Field(default=0, ge=0, description="Results offset")


class FilterTasksRequest(BaseModel):
    """Request model for filtering tasks."""
    status: Optional[List[str]] = Field(default=None, description="Filter by status(es)")
    priority: Optional[List[str]] = Field(default=None, description="Filter by priority(ies)")
    tags: Optional[List[str]] = Field(default=None, description="Filter by tags (any match)")
    tags_all: Optional[List[str]] = Field(default=None, description="Filter by tags (all must match)")
    parent_id: Optional[str] = Field(default=None, description="Filter by parent task ID")
    has_parent: Optional[bool] = Field(default=None, description="Filter by parent existence")
    has_children: Optional[bool] = Field(default=None, description="Filter by children existence")
    has_due_date: Optional[bool] = Field(default=None, description="Filter by due date existence")
    created_after: Optional[str] = Field(default=None, description="Filter created after date (ISO format)")
    created_before: Optional[str] = Field(default=None, description="Filter created before date (ISO format)")
    updated_after: Optional[str] = Field(default=None, description="Filter updated after date (ISO format)")
    updated_before: Optional[str] = Field(default=None, description="Filter updated before date (ISO format)")
    due_after: Optional[str] = Field(default=None, description="Filter due after date (ISO format)")
    due_before: Optional[str] = Field(default=None, description="Filter due before date (ISO format)")
    title_contains: Optional[str] = Field(default=None, description="Filter by title containing text")
    description_contains: Optional[str] = Field(default=None, description="Filter by description containing text")
    include_completed: bool = Field(default=True, description="Include completed tasks")
    limit: Optional[int] = Field(default=None, ge=1, le=1000, description="Maximum results")
    offset: int = Field(default=0, ge=0, description="Results offset")
    sort_by: str = Field(default="created_at", description="Field to sort by")
    sort_desc: bool = Field(default=True, description="Sort in descending order")


class TaskStatisticsResponse(BaseModel):
    """Response model for task statistics."""
    total_tasks: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]
    with_due_dates: int
    overdue: int
    created_today: int
    updated_today: int
    completed_today: int


class ToolResponse(BaseModel):
    """Standard tool response format."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


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


class SearchResultResponse(BaseModel):
    """Response model for search results."""
    tasks: List[TaskResponse]
    total_count: int
    filtered_count: int
    has_more: bool
    offset: int
    limit: Optional[int]
    search_time_ms: Optional[float]


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


def _parse_status_list(status_list: List[str]) -> List[TaskStatus]:
    """Parse list of status strings to TaskStatus enums."""
    result = []
    for status_str in status_list:
        try:
            result.append(TaskStatus.from_string(status_str))
        except ValueError:
            raise ValidationError(f"Invalid status: {status_str}. Must be one of: pending, in_progress, completed, blocked")
    return result


def _parse_priority_list(priority_list: List[str]) -> List[Priority]:
    """Parse list of priority strings to Priority enums."""
    result = []
    for priority_str in priority_list:
        try:
            result.append(Priority.from_string(priority_str))
        except ValueError:
            raise ValidationError(f"Invalid priority: {priority_str}. Must be one of: low, medium, high, urgent")
    return result


def _parse_datetime(date_str: str) -> datetime:
    """Parse ISO datetime string."""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        raise ValidationError(f"Invalid datetime format: {date_str}. Use ISO format (e.g., 2024-01-20T17:00:00Z)")


def _search_result_to_response(result: TaskSearchResult) -> SearchResultResponse:
    """Convert TaskSearchResult to SearchResultResponse."""
    return SearchResultResponse(
        tasks=[_task_to_response(task) for task in result.tasks],
        total_count=result.total_count,
        filtered_count=result.filtered_count,
        has_more=result.has_more,
        offset=result.offset,
        limit=result.limit,
        search_time_ms=result.search_time_ms
    )


async def search_tasks(
    search_text: str,
    search_fields: Optional[List[str]] = None,
    status: Optional[List[str]] = None,
    priority: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    include_completed: bool = True,
    limit: Optional[int] = None,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    Search tasks by text query with optional filtering.
    
    Args:
        search_text: Text to search for in tasks
        search_fields: Fields to search in (title, description, tags)
        status: Filter by status(es)
        priority: Filter by priority(ies)
        tags: Filter by tags
        include_completed: Include completed tasks
        limit: Maximum number of results
        offset: Number of results to skip
        
    Returns:
        Search results with matching tasks
    """
    try:
        # Validate input using Pydantic
        request = SearchTasksRequest(
            search_text=search_text,
            search_fields=search_fields,
            status=status,
            priority=priority,
            tags=tags,
            include_completed=include_completed,
            limit=limit,
            offset=offset
        )
        
        # Get task service
        service = await _get_task_service()
        
        # Build filter parameters
        filter_params = {
            'search_text': request.search_text,
            'include_completed': request.include_completed,
            'limit': request.limit,
            'offset': request.offset
        }
        
        # Add status filter if provided
        if request.status:
            filter_params['status'] = _parse_status_list(request.status)
        
        # Add priority filter if provided
        if request.priority:
            filter_params['priority'] = _parse_priority_list(request.priority)
        
        # Add tags filter if provided
        if request.tags:
            filter_params['tags'] = request.tags
        
        # Handle search fields (for now, we search all fields)
        # TODO: Implement field-specific search when supported by TaskFilter
        
        # Create filter and search
        task_filter = TaskFilter(**filter_params)
        result = await service.filter_tasks(task_filter)
        
        # Convert to response format
        response_data = _search_result_to_response(result)
        
        # Return response
        response = ToolResponse(
            success=True,
            data=response_data.model_dump(),
            message=f"Found {result.total_count} tasks matching search criteria"
        )
        
        logger.info(f"Search completed: '{search_text}' returned {result.total_count} results")
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
        error_msg = f"Unexpected error searching tasks: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def filter_tasks(
    status: Optional[List[str]] = None,
    priority: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    tags_all: Optional[List[str]] = None,
    parent_id: Optional[str] = None,
    has_parent: Optional[bool] = None,
    has_children: Optional[bool] = None,
    has_due_date: Optional[bool] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    updated_after: Optional[str] = None,
    updated_before: Optional[str] = None,
    due_after: Optional[str] = None,
    due_before: Optional[str] = None,
    title_contains: Optional[str] = None,
    description_contains: Optional[str] = None,
    include_completed: bool = True,
    limit: Optional[int] = None,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_desc: bool = True,
) -> Dict[str, Any]:
    """
    Filter tasks by various criteria with advanced options.
    
    Args:
        status: Filter by status(es)
        priority: Filter by priority(ies)
        tags: Filter by tags (any match)
        tags_all: Filter by tags (all must match)
        parent_id: Filter by parent task ID
        has_parent: Filter by parent existence
        has_children: Filter by children existence
        has_due_date: Filter by due date existence
        created_after: Filter created after date (ISO format)
        created_before: Filter created before date (ISO format)
        updated_after: Filter updated after date (ISO format)
        updated_before: Filter updated before date (ISO format)
        due_after: Filter due after date (ISO format)
        due_before: Filter due before date (ISO format)
        title_contains: Filter by title containing text
        description_contains: Filter by description containing text
        include_completed: Include completed tasks
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Field to sort by
        sort_desc: Sort in descending order
        
    Returns:
        Filtered task results
    """
    try:
        # Validate input using Pydantic
        request = FilterTasksRequest(
            status=status,
            priority=priority,
            tags=tags,
            tags_all=tags_all,
            parent_id=parent_id,
            has_parent=has_parent,
            has_children=has_children,
            has_due_date=has_due_date,
            created_after=created_after,
            created_before=created_before,
            updated_after=updated_after,
            updated_before=updated_before,
            due_after=due_after,
            due_before=due_before,
            title_contains=title_contains,
            description_contains=description_contains,
            include_completed=include_completed,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
        
        # Get task service
        service = await _get_task_service()
        
        # Build filter parameters
        filter_params = {
            'include_completed': request.include_completed,
            'limit': request.limit,
            'offset': request.offset,
            'sort_by': request.sort_by,
            'sort_desc': request.sort_desc
        }
        
        # Add filters if provided
        if request.status:
            filter_params['status'] = _parse_status_list(request.status)
        
        if request.priority:
            filter_params['priority'] = _parse_priority_list(request.priority)
        
        if request.tags:
            filter_params['tags'] = request.tags
        
        if request.tags_all:
            filter_params['tags_all'] = request.tags_all
        
        if request.parent_id is not None:
            filter_params['parent_id'] = request.parent_id
        
        if request.has_parent is not None:
            filter_params['has_parent'] = request.has_parent
        
        if request.has_children is not None:
            filter_params['has_children'] = request.has_children
        
        if request.has_due_date is not None:
            filter_params['has_due_date'] = request.has_due_date
        
        # Parse date filters
        if request.created_after:
            filter_params['created_after'] = _parse_datetime(request.created_after)
        
        if request.created_before:
            filter_params['created_before'] = _parse_datetime(request.created_before)
        
        if request.updated_after:
            filter_params['updated_after'] = _parse_datetime(request.updated_after)
        
        if request.updated_before:
            filter_params['updated_before'] = _parse_datetime(request.updated_before)
        
        if request.due_after:
            filter_params['due_after'] = _parse_datetime(request.due_after)
        
        if request.due_before:
            filter_params['due_before'] = _parse_datetime(request.due_before)
        
        # Add text filters
        if request.title_contains:
            filter_params['title_contains'] = request.title_contains
        
        if request.description_contains:
            filter_params['description_contains'] = request.description_contains
        
        # Create filter and execute
        task_filter = TaskFilter(**filter_params)
        result = await service.filter_tasks(task_filter)
        
        # Convert to response format
        response_data = _search_result_to_response(result)
        
        # Return response
        response = ToolResponse(
            success=True,
            data=response_data.model_dump(),
            message=f"Filtered {result.total_count} tasks with specified criteria"
        )
        
        logger.info(f"Filter completed: returned {result.total_count} results")
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
        error_msg = f"Unexpected error filtering tasks: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def get_task_statistics() -> Dict[str, Any]:
    """
    Get comprehensive statistics about all tasks.
    
    Returns:
        Task statistics including counts by status, priority, dates, etc.
    """
    try:
        # Get task service
        service = await _get_task_service()
        
        # Get statistics from service
        stats = await service.get_task_statistics()
        
        # Check for error in statistics
        if 'error' in stats:
            return ToolResponse(
                success=False,
                error=f"Failed to get statistics: {stats['error']}"
            ).model_dump()
        
        # Validate and format response
        stats_response = TaskStatisticsResponse(
            total_tasks=stats.get('total_tasks', 0),
            by_status=stats.get('by_status', {}),
            by_priority=stats.get('by_priority', {}),
            with_due_dates=stats.get('with_due_dates', 0),
            overdue=stats.get('overdue', 0),
            created_today=stats.get('created_today', 0),
            updated_today=stats.get('updated_today', 0),
            completed_today=stats.get('completed_today', 0)
        )
        
        # Return response
        response = ToolResponse(
            success=True,
            data=stats_response.model_dump(),
            message=f"Retrieved statistics for {stats_response.total_tasks} tasks"
        )
        
        logger.info(f"Statistics retrieved: {stats_response.total_tasks} total tasks")
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
        error_msg = f"Unexpected error getting statistics: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()