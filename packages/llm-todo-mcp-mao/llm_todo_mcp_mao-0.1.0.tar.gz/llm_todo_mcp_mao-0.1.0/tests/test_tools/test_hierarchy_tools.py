"""
Tests for hierarchy management tools.

This module tests the MCP tools for managing task hierarchies,
including parent-child relationships and hierarchy operations.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import ValidationError

from src.todo_mcp.tools.hierarchy_tools import (
    add_child_task,
    remove_child_task,
    get_task_hierarchy,
    move_task,
    _hierarchy_node_to_response,
    _calculate_subtree_depth,
    AddChildTaskRequest,
    RemoveChildTaskRequest,
    GetTaskHierarchyRequest,
    MoveTaskRequest,
    HierarchyNodeResponse,
    ToolResponse
)
from src.todo_mcp.models.task import Task
from src.todo_mcp.models.status import TaskStatus, Priority


@pytest.fixture
def sample_tasks():
    """Create sample tasks for testing."""
    return [
        Task(
            id="parent1",
            title="Parent Task 1",
            description="Parent task description",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.HIGH,
            child_ids=["child1", "child2"]
        ),
        Task(
            id="child1",
            title="Child Task 1",
            description="Child task 1 description",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            parent_id="parent1"
        ),
        Task(
            id="child2",
            title="Child Task 2",
            description="Child task 2 description",
            status=TaskStatus.COMPLETED,
            priority=Priority.LOW,
            parent_id="parent1"
        ),
        Task(
            id="orphan1",
            title="Orphan Task",
            description="Task without parent",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM
        )
    ]


@pytest.fixture
def mock_services():
    """Create mock task and hierarchy services."""
    task_service = AsyncMock()
    hierarchy_service = MagicMock()
    return task_service, hierarchy_service


class TestPydanticModels:
    """Test Pydantic model validation for hierarchy tools."""
    
    def test_add_child_task_request_valid(self):
        """Test valid AddChildTaskRequest creation."""
        request = AddChildTaskRequest(parent_id="parent1", child_id="child1")
        assert request.parent_id == "parent1"
        assert request.child_id == "child1"
    
    def test_add_child_task_request_validation(self):
        """Test AddChildTaskRequest validation."""
        with pytest.raises(ValidationError):
            AddChildTaskRequest(parent_id="", child_id="child1")
        
        with pytest.raises(ValidationError):
            AddChildTaskRequest(parent_id="parent1", child_id="")
    
    def test_remove_child_task_request_valid(self):
        """Test valid RemoveChildTaskRequest creation."""
        request = RemoveChildTaskRequest(parent_id="parent1", child_id="child1")
        assert request.parent_id == "parent1"
        assert request.child_id == "child1"
    
    def test_get_task_hierarchy_request_valid(self):
        """Test valid GetTaskHierarchyRequest creation."""
        request = GetTaskHierarchyRequest(
            task_id="task1",
            max_depth=3,
            include_ancestors=True
        )
        assert request.task_id == "task1"
        assert request.max_depth == 3
        assert request.include_ancestors is True
    
    def test_get_task_hierarchy_request_defaults(self):
        """Test GetTaskHierarchyRequest with defaults."""
        request = GetTaskHierarchyRequest(task_id="task1")
        assert request.task_id == "task1"
        assert request.max_depth is None
        assert request.include_ancestors is False
    
    def test_move_task_request_valid(self):
        """Test valid MoveTaskRequest creation."""
        request = MoveTaskRequest(task_id="task1", new_parent_id="parent1")
        assert request.task_id == "task1"
        assert request.new_parent_id == "parent1"
    
    def test_move_task_request_root_level(self):
        """Test MoveTaskRequest for root level move."""
        request = MoveTaskRequest(task_id="task1", new_parent_id=None)
        assert request.task_id == "task1"
        assert request.new_parent_id is None
    
    def test_hierarchy_node_response_creation(self):
        """Test HierarchyNodeResponse creation."""
        response = HierarchyNodeResponse(
            task_id="task1",
            title="Test Task",
            status="pending",
            priority="medium",
            depth=1,
            has_parent=True,
            child_count=2
        )
        assert response.task_id == "task1"
        assert response.title == "Test Task"
        assert response.depth == 1
        assert response.has_parent is True
        assert response.child_count == 2
        assert response.children is None
    
    def test_hierarchy_node_response_with_children(self):
        """Test HierarchyNodeResponse with children."""
        child = HierarchyNodeResponse(
            task_id="child1",
            title="Child Task",
            status="pending",
            priority="low",
            depth=2,
            has_parent=True,
            child_count=0
        )
        
        parent = HierarchyNodeResponse(
            task_id="parent1",
            title="Parent Task",
            status="in_progress",
            priority="high",
            depth=1,
            has_parent=False,
            child_count=1,
            children=[child]
        )
        
        assert len(parent.children) == 1
        assert parent.children[0].task_id == "child1"


class TestUtilityFunctions:
    """Test utility functions for hierarchy tools."""
    
    def test_hierarchy_node_to_response(self):
        """Test conversion from hierarchy node dict to response."""
        node_dict = {
            "task": {
                "id": "task1",
                "title": "Test Task",
                "status": "pending",
                "priority": "medium"
            },
            "depth": 1,
            "has_parent": True,
            "child_count": 2,
            "children": [
                {
                    "task": {
                        "id": "child1",
                        "title": "Child Task",
                        "status": "completed",
                        "priority": "low"
                    },
                    "depth": 2,
                    "has_parent": True,
                    "child_count": 0
                }
            ]
        }
        
        response = _hierarchy_node_to_response(node_dict)
        
        assert response.task_id == "task1"
        assert response.title == "Test Task"
        assert response.status == "pending"
        assert response.priority == "medium"
        assert response.depth == 1
        assert response.has_parent is True
        assert response.child_count == 2
        assert len(response.children) == 1
        assert response.children[0].task_id == "child1"
    
    def test_calculate_subtree_depth_no_children(self):
        """Test subtree depth calculation with no children."""
        node_dict = {
            "task": {"id": "task1"},
            "children": []
        }
        
        depth = _calculate_subtree_depth(node_dict)
        assert depth == 0
    
    def test_calculate_subtree_depth_with_children(self):
        """Test subtree depth calculation with children."""
        node_dict = {
            "task": {"id": "parent"},
            "children": [
                {
                    "task": {"id": "child1"},
                    "children": [
                        {
                            "task": {"id": "grandchild1"},
                            "children": []
                        }
                    ]
                },
                {
                    "task": {"id": "child2"},
                    "children": []
                }
            ]
        }
        
        depth = _calculate_subtree_depth(node_dict)
        assert depth == 2  # parent -> child1 -> grandchild1


class TestAddChildTask:
    """Test add_child_task tool."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_add_child_task_success(self, mock_get_services, sample_tasks):
        """Test successful child task addition."""
        task_service, hierarchy_service = AsyncMock(), MagicMock()
        mock_get_services.return_value = (task_service, hierarchy_service)
        
        # Setup mocks
        parent_task = sample_tasks[0]  # parent1
        child_task = sample_tasks[3]   # orphan1
        
        task_service.get_task.side_effect = lambda task_id: {
            "parent1": parent_task,
            "orphan1": child_task
        }.get(task_id)
        
        task_service.list_tasks.return_value = sample_tasks
        hierarchy_service.validate_hierarchy_operation.return_value = True
        hierarchy_service.add_parent_child_relationship.return_value = True
        hierarchy_service.get_subtree.return_value = {"task": parent_task.model_dump(), "depth": 0, "has_parent": False, "child_count": 1}
        
        # Execute
        result = await add_child_task("parent1", "orphan1")
        
        # Verify
        assert result["success"] is True
        assert result["data"]["parent_id"] == "parent1"
        assert result["data"]["child_id"] == "orphan1"
        assert "Successfully added child task" in result["message"]
        
        # Verify service calls
        hierarchy_service.validate_hierarchy_operation.assert_called_once_with("parent1", "orphan1", sample_tasks)
        hierarchy_service.add_parent_child_relationship.assert_called_once_with("parent1", "orphan1", sample_tasks)
        task_service.save_task.assert_called()
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_add_child_task_parent_not_found(self, mock_get_services):
        """Test add child task with non-existent parent."""
        task_service, hierarchy_service = AsyncMock(), MagicMock()
        mock_get_services.return_value = (task_service, hierarchy_service)
        
        task_service.get_task.return_value = None
        
        result = await add_child_task("nonexistent", "child1")
        
        assert result["success"] is False
        assert "Parent task not found" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_add_child_task_child_not_found(self, mock_get_services, sample_tasks):
        """Test add child task with non-existent child."""
        task_service, hierarchy_service = AsyncMock(), MagicMock()
        mock_get_services.return_value = (task_service, hierarchy_service)
        
        parent_task = sample_tasks[0]
        task_service.get_task.side_effect = lambda task_id: parent_task if task_id == "parent1" else None
        
        result = await add_child_task("parent1", "nonexistent")
        
        assert result["success"] is False
        assert "Child task not found" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_add_child_task_would_create_cycle(self, mock_get_services, sample_tasks):
        """Test add child task that would create a cycle."""
        task_service, hierarchy_service = AsyncMock(), MagicMock()
        mock_get_services.return_value = (task_service, hierarchy_service)
        
        parent_task = sample_tasks[0]
        child_task = sample_tasks[1]
        
        task_service.get_task.side_effect = lambda task_id: {
            "parent1": parent_task,
            "child1": child_task
        }.get(task_id)
        
        task_service.list_tasks.return_value = sample_tasks
        hierarchy_service.validate_hierarchy_operation.return_value = False
        
        result = await add_child_task("child1", "parent1")  # Would create cycle
        
        assert result["success"] is False
        assert "would create a cycle" in result["error"]


class TestRemoveChildTask:
    """Test remove_child_task tool."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_remove_child_task_success(self, mock_get_services, sample_tasks):
        """Test successful child task removal."""
        task_service, hierarchy_service = AsyncMock(), MagicMock()
        mock_get_services.return_value = (task_service, hierarchy_service)
        
        parent_task = sample_tasks[0]  # parent1 with child1, child2
        child_task = sample_tasks[1]   # child1
        
        task_service.get_task.side_effect = lambda task_id: {
            "parent1": parent_task,
            "child1": child_task
        }.get(task_id)
        
        task_service.list_tasks.return_value = sample_tasks
        hierarchy_service.remove_parent_child_relationship.return_value = True
        
        result = await remove_child_task("parent1", "child1")
        
        assert result["success"] is True
        assert result["data"]["parent_id"] == "parent1"
        assert result["data"]["child_id"] == "child1"
        assert result["data"]["removed"] is True
        assert "Successfully removed child task" in result["message"]
        
        hierarchy_service.remove_parent_child_relationship.assert_called_once_with("parent1", "child1", sample_tasks)
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_remove_child_task_not_a_child(self, mock_get_services, sample_tasks):
        """Test removing a task that is not a child."""
        task_service, hierarchy_service = AsyncMock(), MagicMock()
        mock_get_services.return_value = (task_service, hierarchy_service)
        
        parent_task = sample_tasks[0]  # parent1
        orphan_task = sample_tasks[3]  # orphan1 (not a child)
        
        task_service.get_task.side_effect = lambda task_id: {
            "parent1": parent_task,
            "orphan1": orphan_task
        }.get(task_id)
        
        result = await remove_child_task("parent1", "orphan1")
        
        assert result["success"] is False
        assert "is not a child of" in result["error"]


class TestGetTaskHierarchy:
    """Test get_task_hierarchy tool."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_get_task_hierarchy_success(self, mock_get_services, sample_tasks):
        """Test successful hierarchy retrieval."""
        task_service, hierarchy_service = AsyncMock(), MagicMock()
        mock_get_services.return_value = (task_service, hierarchy_service)
        
        task = sample_tasks[0]  # parent1
        task_service.get_task.return_value = task
        task_service.list_tasks.return_value = sample_tasks
        
        # Mock hierarchy data
        hierarchy_data = {
            "task": {
                "id": "parent1",
                "title": "Parent Task 1",
                "status": "in_progress",
                "priority": "high"
            },
            "depth": 0,
            "has_parent": False,
            "child_count": 2,
            "children": [
                {
                    "task": {
                        "id": "child1",
                        "title": "Child Task 1",
                        "status": "pending",
                        "priority": "medium"
                    },
                    "depth": 1,
                    "has_parent": True,
                    "child_count": 0
                }
            ]
        }
        
        hierarchy_service.get_subtree.return_value = hierarchy_data
        hierarchy_service.get_hierarchy_statistics.return_value = {"max_depth": 2}
        hierarchy_service.get_task_descendants_list.return_value = [sample_tasks[1], sample_tasks[2]]
        
        result = await get_task_hierarchy("parent1")
        
        assert result["success"] is True
        assert result["data"]["root_task"]["task_id"] == "parent1"
        assert result["data"]["total_nodes"] == 3  # parent + 2 descendants
        assert len(result["data"]["root_task"]["children"]) == 1
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_get_task_hierarchy_with_ancestors(self, mock_get_services, sample_tasks):
        """Test hierarchy retrieval with ancestors."""
        task_service, hierarchy_service = AsyncMock(), MagicMock()
        mock_get_services.return_value = (task_service, hierarchy_service)
        
        task = sample_tasks[1]  # child1
        task_service.get_task.return_value = task
        task_service.list_tasks.return_value = sample_tasks
        
        hierarchy_data = {
            "task": {
                "id": "child1",
                "title": "Child Task 1",
                "status": "pending",
                "priority": "medium"
            },
            "depth": 1,
            "has_parent": True,
            "child_count": 0
        }
        
        hierarchy_service.get_subtree.return_value = hierarchy_data
        hierarchy_service.get_hierarchy_statistics.return_value = {"max_depth": 2}
        hierarchy_service.get_task_descendants_list.return_value = []
        hierarchy_service.get_task_ancestors_list.return_value = [sample_tasks[0]]  # parent1
        
        result = await get_task_hierarchy("child1", include_ancestors=True)
        
        assert result["success"] is True
        assert "ancestors" in result["data"]
        hierarchy_service.get_task_ancestors_list.assert_called_once_with("child1", sample_tasks)
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_get_task_hierarchy_task_not_found(self, mock_get_services):
        """Test hierarchy retrieval for non-existent task."""
        task_service, hierarchy_service = AsyncMock(), MagicMock()
        mock_get_services.return_value = (task_service, hierarchy_service)
        
        task_service.get_task.return_value = None
        
        result = await get_task_hierarchy("nonexistent")
        
        assert result["success"] is False
        assert "Task not found" in result["error"]


class TestMoveTask:
    """Test move_task tool."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_move_task_to_new_parent_success(self, mock_get_services, sample_tasks):
        """Test successful task move to new parent."""
        task_service, hierarchy_service = AsyncMock(), MagicMock()
        mock_get_services.return_value = (task_service, hierarchy_service)
        
        task_to_move = sample_tasks[3]  # orphan1
        new_parent = sample_tasks[0]    # parent1
        
        task_service.get_task.side_effect = lambda task_id: {
            "orphan1": task_to_move,
            "parent1": new_parent
        }.get(task_id)
        
        task_service.list_tasks.return_value = sample_tasks
        hierarchy_service.move_task_to_parent.return_value = True
        hierarchy_service.get_subtree.return_value = {"task": new_parent.model_dump(), "depth": 0, "has_parent": False, "child_count": 1}
        
        result = await move_task("orphan1", "parent1")
        
        assert result["success"] is True
        assert result["data"]["task_id"] == "orphan1"
        assert result["data"]["new_parent_id"] == "parent1"
        assert "Successfully moved task" in result["message"]
        
        hierarchy_service.move_task_to_parent.assert_called_once_with("orphan1", "parent1", sample_tasks)
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_move_task_to_root_level(self, mock_get_services, sample_tasks):
        """Test moving task to root level."""
        task_service, hierarchy_service = AsyncMock(), MagicMock()
        mock_get_services.return_value = (task_service, hierarchy_service)
        
        task_to_move = sample_tasks[1]  # child1 (has parent)
        
        task_service.get_task.return_value = task_to_move
        task_service.list_tasks.return_value = sample_tasks
        hierarchy_service.move_task_to_parent.return_value = True
        hierarchy_service.get_subtree.return_value = {"task": task_to_move.model_dump(), "depth": 0, "has_parent": False, "child_count": 0}
        
        result = await move_task("child1", None)
        
        assert result["success"] is True
        assert result["data"]["task_id"] == "child1"
        assert result["data"]["new_parent_id"] is None
        assert "root level" in result["message"]
        
        hierarchy_service.move_task_to_parent.assert_called_once_with("child1", None, sample_tasks)
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_move_task_not_found(self, mock_get_services):
        """Test moving non-existent task."""
        task_service, hierarchy_service = AsyncMock(), MagicMock()
        mock_get_services.return_value = (task_service, hierarchy_service)
        
        task_service.get_task.return_value = None
        
        result = await move_task("nonexistent", "parent1")
        
        assert result["success"] is False
        assert "Task not found" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_move_task_new_parent_not_found(self, mock_get_services, sample_tasks):
        """Test moving task to non-existent parent."""
        task_service, hierarchy_service = AsyncMock(), MagicMock()
        mock_get_services.return_value = (task_service, hierarchy_service)
        
        task_to_move = sample_tasks[3]  # orphan1
        
        task_service.get_task.side_effect = lambda task_id: task_to_move if task_id == "orphan1" else None
        
        result = await move_task("orphan1", "nonexistent")
        
        assert result["success"] is False
        assert "New parent task not found" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_move_task_operation_failed(self, mock_get_services, sample_tasks):
        """Test move task when hierarchy service operation fails."""
        task_service, hierarchy_service = AsyncMock(), MagicMock()
        mock_get_services.return_value = (task_service, hierarchy_service)
        
        task_to_move = sample_tasks[3]  # orphan1
        new_parent = sample_tasks[0]    # parent1
        
        task_service.get_task.side_effect = lambda task_id: {
            "orphan1": task_to_move,
            "parent1": new_parent
        }.get(task_id)
        
        task_service.list_tasks.return_value = sample_tasks
        hierarchy_service.move_task_to_parent.return_value = False  # Operation failed
        
        result = await move_task("orphan1", "parent1")
        
        assert result["success"] is False
        assert "Failed to move task" in result["error"]


class TestErrorHandling:
    """Test error handling in hierarchy tools."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_validation_error_handling(self, mock_get_services):
        """Test handling of Pydantic validation errors."""
        # This would be caught by Pydantic validation before reaching the function
        # but we can test the error response format
        result = await add_child_task("", "child1")  # Empty parent_id
        
        assert result["success"] is False
        assert "Validation error" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.hierarchy_tools._get_services')
    async def test_service_error_handling(self, mock_get_services):
        """Test handling of service errors."""
        task_service, hierarchy_service = AsyncMock(), MagicMock()
        mock_get_services.return_value = (task_service, hierarchy_service)
        
        # Mock service to raise an exception
        task_service.get_task.side_effect = Exception("Service error")
        
        result = await add_child_task("parent1", "child1")
        
        assert result["success"] is False
        assert "Unexpected error" in result["error"]