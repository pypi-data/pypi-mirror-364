"""
MCP tools for task hierarchy management.

This module provides MCP-compatible tools for managing parent-child
relationships between tasks with Pydantic validation.
"""

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError

from ..config import TodoConfig
from ..services.task_service import TaskService, TaskServiceError, TaskNotFoundError
from ..services.hierarchy_service import HierarchyService


# Global service instances
_task_service: Optional[TaskService] = None
_hierarchy_service: Optional[HierarchyService] = None
_config: Optional[TodoConfig] = None

logger = logging.getLogger(__name__)


async def _get_services() -> tuple[TaskService, HierarchyService]:
    """Get or initialize the task and hierarchy services."""
    global _task_service, _hierarchy_service, _config
    
    if _task_service is None or _hierarchy_service is None:
        from ..config import config
        _config = config
        _task_service = TaskService(_config)
        _hierarchy_service = HierarchyService(_config)
        await _task_service.initialize()
    
    return _task_service, _hierarchy_service


# Pydantic models for tool parameters and responses

class AddChildTaskRequest(BaseModel):
    """Request model for adding a child task."""
    parent_id: str = Field(..., min_length=1, description="Parent task ID")
    child_id: str = Field(..., min_length=1, description="Child task ID to add")


class RemoveChildTaskRequest(BaseModel):
    """Request model for removing a child task."""
    parent_id: str = Field(..., min_length=1, description="Parent task ID")
    child_id: str = Field(..., min_length=1, description="Child task ID to remove")


class GetTaskHierarchyRequest(BaseModel):
    """Request model for getting task hierarchy."""
    task_id: str = Field(..., min_length=1, description="Root task ID for hierarchy")
    max_depth: Optional[int] = Field(default=None, description="Maximum depth to traverse")
    include_ancestors: bool = Field(default=False, description="Include ancestor tasks")


class MoveTaskRequest(BaseModel):
    """Request model for moving a task."""
    task_id: str = Field(..., min_length=1, description="Task ID to move")
    new_parent_id: Optional[str] = Field(default=None, description="New parent task ID (None for root level)")


class HierarchyNodeResponse(BaseModel):
    """Response model for hierarchy node data."""
    task_id: str
    title: str
    status: str
    priority: str
    depth: int
    has_parent: bool
    child_count: int
    children: Optional[List['HierarchyNodeResponse']] = None


class HierarchyResponse(BaseModel):
    """Response model for hierarchy data."""
    root_task: HierarchyNodeResponse
    total_nodes: int
    max_depth: int
    ancestors: Optional[List[HierarchyNodeResponse]] = None


class ToolResponse(BaseModel):
    """Standard tool response format."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


def _hierarchy_node_to_response(node_dict: Dict[str, Any]) -> HierarchyNodeResponse:
    """Convert hierarchy node dictionary to response model."""
    task_data = node_dict["task"]
    
    response = HierarchyNodeResponse(
        task_id=task_data["id"],
        title=task_data["title"],
        status=task_data["status"],
        priority=task_data["priority"],
        depth=node_dict["depth"],
        has_parent=node_dict["has_parent"],
        child_count=node_dict["child_count"]
    )
    
    # Add children if present
    if "children" in node_dict and node_dict["children"]:
        response.children = [
            _hierarchy_node_to_response(child) 
            for child in node_dict["children"]
        ]
    
    return response


async def add_child_task(parent_id: str, child_id: str) -> Dict[str, Any]:
    """
    Add a child task to a parent task.
    
    Args:
        parent_id: Parent task ID
        child_id: Child task ID
        
    Returns:
        Operation result with updated hierarchy information
    """
    try:
        # Validate input using Pydantic
        request = AddChildTaskRequest(parent_id=parent_id, child_id=child_id)
        
        # Get services
        task_service, hierarchy_service = await _get_services()
        
        # Validate that both tasks exist
        parent_task = await task_service.get_task(request.parent_id)
        if not parent_task:
            return ToolResponse(
                success=False,
                error=f"Parent task not found: {request.parent_id}"
            ).model_dump()
        
        child_task = await task_service.get_task(request.child_id)
        if not child_task:
            return ToolResponse(
                success=False,
                error=f"Child task not found: {request.child_id}"
            ).model_dump()
        
        # Get all tasks for hierarchy validation
        all_tasks = await task_service.list_tasks()
        
        # Validate the hierarchy operation
        if not hierarchy_service.validate_hierarchy_operation(
            request.parent_id, request.child_id, all_tasks
        ):
            return ToolResponse(
                success=False,
                error=f"Cannot add child {request.child_id} to parent {request.parent_id}: would create a cycle"
            ).model_dump()
        
        # Add the parent-child relationship
        success = hierarchy_service.add_parent_child_relationship(
            request.parent_id, request.child_id, all_tasks
        )
        
        if not success:
            return ToolResponse(
                success=False,
                error="Failed to add parent-child relationship"
            ).model_dump()
        
        # Save the updated tasks
        await task_service.save_task(parent_task)
        await task_service.save_task(child_task)
        
        # Get updated hierarchy for response
        hierarchy_data = hierarchy_service.get_subtree(request.parent_id, all_tasks, max_depth=2)
        
        response = ToolResponse(
            success=True,
            data={
                "parent_id": request.parent_id,
                "child_id": request.child_id,
                "hierarchy": hierarchy_data
            },
            message=f"Successfully added child task {request.child_id} to parent {request.parent_id}"
        )
        
        logger.info(f"Added child task {request.child_id} to parent {request.parent_id}")
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
        error_msg = f"Unexpected error adding child task: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def remove_child_task(parent_id: str, child_id: str) -> Dict[str, Any]:
    """
    Remove a child task from a parent task.
    
    Args:
        parent_id: Parent task ID
        child_id: Child task ID to remove
        
    Returns:
        Operation result
    """
    try:
        # Validate input using Pydantic
        request = RemoveChildTaskRequest(parent_id=parent_id, child_id=child_id)
        
        # Get services
        task_service, hierarchy_service = await _get_services()
        
        # Validate that both tasks exist
        parent_task = await task_service.get_task(request.parent_id)
        if not parent_task:
            return ToolResponse(
                success=False,
                error=f"Parent task not found: {request.parent_id}"
            ).model_dump()
        
        child_task = await task_service.get_task(request.child_id)
        if not child_task:
            return ToolResponse(
                success=False,
                error=f"Child task not found: {request.child_id}"
            ).model_dump()
        
        # Check if the relationship exists
        if request.child_id not in parent_task.child_ids:
            return ToolResponse(
                success=False,
                error=f"Task {request.child_id} is not a child of {request.parent_id}"
            ).model_dump()
        
        # Get all tasks for hierarchy operations
        all_tasks = await task_service.list_tasks()
        
        # Remove the parent-child relationship
        success = hierarchy_service.remove_parent_child_relationship(
            request.parent_id, request.child_id, all_tasks
        )
        
        if not success:
            return ToolResponse(
                success=False,
                error="Failed to remove parent-child relationship"
            ).model_dump()
        
        # Save the updated tasks
        await task_service.save_task(parent_task)
        await task_service.save_task(child_task)
        
        response = ToolResponse(
            success=True,
            data={
                "parent_id": request.parent_id,
                "child_id": request.child_id,
                "removed": True
            },
            message=f"Successfully removed child task {request.child_id} from parent {request.parent_id}"
        )
        
        logger.info(f"Removed child task {request.child_id} from parent {request.parent_id}")
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
        error_msg = f"Unexpected error removing child task: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def get_task_hierarchy(
    task_id: str, 
    max_depth: Optional[int] = None,
    include_ancestors: bool = False
) -> Dict[str, Any]:
    """
    Get the complete hierarchy for a task.
    
    Args:
        task_id: Root task ID for hierarchy
        max_depth: Maximum depth to traverse
        include_ancestors: Include ancestor tasks in response
        
    Returns:
        Hierarchical task structure
    """
    try:
        # Validate input using Pydantic
        request = GetTaskHierarchyRequest(
            task_id=task_id,
            max_depth=max_depth,
            include_ancestors=include_ancestors
        )
        
        # Get services
        task_service, hierarchy_service = await _get_services()
        
        # Validate that task exists
        task = await task_service.get_task(request.task_id)
        if not task:
            return ToolResponse(
                success=False,
                error=f"Task not found: {request.task_id}"
            ).model_dump()
        
        # Get all tasks for hierarchy building
        all_tasks = await task_service.list_tasks()
        
        # Get the subtree starting from the task
        subtree_data = hierarchy_service.get_subtree(
            request.task_id, all_tasks, max_depth=request.max_depth
        )
        
        if not subtree_data:
            return ToolResponse(
                success=False,
                error=f"Could not build hierarchy for task: {request.task_id}"
            ).model_dump()
        
        # Convert to response format
        root_node = _hierarchy_node_to_response(subtree_data)
        
        # Get hierarchy statistics
        stats = hierarchy_service.get_hierarchy_statistics(all_tasks)
        
        # Build response data
        response_data = {
            "root_task": root_node.model_dump(),
            "total_nodes": len(hierarchy_service.get_task_descendants_list(request.task_id, all_tasks)) + 1,
            "max_depth": subtree_data.get("depth", 0) + _calculate_subtree_depth(subtree_data)
        }
        
        # Add ancestors if requested
        if request.include_ancestors:
            ancestors = hierarchy_service.get_task_ancestors_list(request.task_id, all_tasks)
            ancestor_responses = []
            
            for ancestor in ancestors:
                ancestor_node = hierarchy_service.get_subtree(ancestor.id, all_tasks, max_depth=1)
                if ancestor_node:
                    ancestor_responses.append(_hierarchy_node_to_response(ancestor_node).model_dump())
            
            response_data["ancestors"] = ancestor_responses
        
        response = ToolResponse(
            success=True,
            data=response_data,
            message=f"Retrieved hierarchy for task {request.task_id}"
        )
        
        return response.model_dump()
        
    except ValidationError as e:
        error_msg = f"Validation error: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()
    
    except Exception as e:
        error_msg = f"Unexpected error getting task hierarchy: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


async def move_task(task_id: str, new_parent_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Move a task to a new parent (or to root level).
    
    Args:
        task_id: Task ID to move
        new_parent_id: New parent task ID (None for root level)
        
    Returns:
        Operation result with updated hierarchy information
    """
    try:
        # Validate input using Pydantic
        request = MoveTaskRequest(task_id=task_id, new_parent_id=new_parent_id)
        
        # Get services
        task_service, hierarchy_service = await _get_services()
        
        # Validate that task exists
        task = await task_service.get_task(request.task_id)
        if not task:
            return ToolResponse(
                success=False,
                error=f"Task not found: {request.task_id}"
            ).model_dump()
        
        # Validate new parent exists if specified
        if request.new_parent_id:
            new_parent = await task_service.get_task(request.new_parent_id)
            if not new_parent:
                return ToolResponse(
                    success=False,
                    error=f"New parent task not found: {request.new_parent_id}"
                ).model_dump()
        
        # Get all tasks for hierarchy operations
        all_tasks = await task_service.list_tasks()
        
        # Store old parent for response
        old_parent_id = task.parent_id
        
        # Move the task
        success = hierarchy_service.move_task_to_parent(
            request.task_id, request.new_parent_id, all_tasks
        )
        
        if not success:
            return ToolResponse(
                success=False,
                error=f"Failed to move task {request.task_id} to new parent"
            ).model_dump()
        
        # Save the updated task
        await task_service.save_task(task)
        
        # Save old parent if it existed
        if old_parent_id:
            old_parent = await task_service.get_task(old_parent_id)
            if old_parent:
                await task_service.save_task(old_parent)
        
        # Save new parent if it exists
        if request.new_parent_id:
            new_parent = await task_service.get_task(request.new_parent_id)
            if new_parent:
                await task_service.save_task(new_parent)
        
        # Get updated hierarchy for response
        hierarchy_data = None
        if request.new_parent_id:
            hierarchy_data = hierarchy_service.get_subtree(request.new_parent_id, all_tasks, max_depth=2)
        else:
            hierarchy_data = hierarchy_service.get_subtree(request.task_id, all_tasks, max_depth=2)
        
        response = ToolResponse(
            success=True,
            data={
                "task_id": request.task_id,
                "old_parent_id": old_parent_id,
                "new_parent_id": request.new_parent_id,
                "hierarchy": hierarchy_data
            },
            message=f"Successfully moved task {request.task_id} to {'root level' if not request.new_parent_id else f'parent {request.new_parent_id}'}"
        )
        
        logger.info(f"Moved task {request.task_id} from {old_parent_id} to {request.new_parent_id}")
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
        error_msg = f"Unexpected error moving task: {e}"
        logger.error(error_msg)
        return ToolResponse(success=False, error=error_msg).model_dump()


def _calculate_subtree_depth(node_dict: Dict[str, Any]) -> int:
    """Calculate the maximum depth of a subtree."""
    if not node_dict.get("children"):
        return 0
    
    max_child_depth = 0
    for child in node_dict["children"]:
        child_depth = _calculate_subtree_depth(child)
        max_child_depth = max(max_child_depth, child_depth)
    
    return max_child_depth + 1


# Enable forward references for recursive model
HierarchyNodeResponse.model_rebuild()