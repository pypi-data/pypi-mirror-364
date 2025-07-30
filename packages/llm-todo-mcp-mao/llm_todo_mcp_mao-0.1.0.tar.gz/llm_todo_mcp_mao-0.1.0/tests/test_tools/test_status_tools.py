"""
Tests for status management MCP tools.

This module tests the MCP tools for task status management,
including Pydantic validation and error handling.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.todo_mcp.tools.status_tools import (
    update_task_status,
    bulk_status_update,
    get_task_status,
    get_pending_tasks,
    get_in_progress_tasks,
    get_blocked_tasks,
    get_completed_tasks,
)
from src.todo_mcp.models.task import Task
from src.todo_mcp.models.status import TaskStatus, Priority, StatusTransitionError
from src.todo_mcp.services.task_service import TaskServiceError, TaskNotFoundError, TaskValidationError


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    now = datetime.now(timezone.utc)
    future_date = now + timedelta(days=5)
    
    return Task(
        id="test_task_001",
        title="Test Task",
        description="Test task description",
        status=TaskStatus.PENDING,
        priority=Priority.MEDIUM,
        tags=["test", "sample"],
        parent_id=None,
        child_ids=["child_001", "child_002"],
        created_at=now - timedelta(days=1),
        updated_at=now,
        due_date=future_date,
        metadata={"estimated_hours": 8, "complexity": "medium"}
    )


@pytest.fixture
def in_progress_task():
    """Create a sample in-progress task for testing."""
    now = datetime.now(timezone.utc)
    
    return Task(
        id="test_task_002",
        title="In Progress Task",
        description="Task in progress",
        status=TaskStatus.IN_PROGRESS,
        priority=Priority.HIGH,
        tags=["work"],
        created_at=now - timedelta(days=2),
        updated_at=now
    )


@pytest.fixture
def completed_task():
    """Create a sample completed task for testing."""
    now = datetime.now(timezone.utc)
    
    return Task(
        id="test_task_003",
        title="Completed Task",
        description="Task completed",
        status=TaskStatus.COMPLETED,
        priority=Priority.LOW,
        tags=["done"],
        created_at=now - timedelta(days=3),
        updated_at=now
    )


@pytest.fixture
def blocked_task():
    """Create a sample blocked task for testing."""
    now = datetime.now(timezone.utc)
    
    return Task(
        id="test_task_004",
        title="Blocked Task",
        description="Task blocked",
        status=TaskStatus.BLOCKED,
        priority=Priority.URGENT,
        tags=["blocked"],
        created_at=now - timedelta(days=1),
        updated_at=now
    )


# Note: Helper functions are private and tested through public interface


class TestUpdateTaskStatus:
    """Test update_task_status tool."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_update_task_status_success(self, mock_get_service, sample_task):
        """Test successful task status update."""
        # Setup mock
        mock_service = AsyncMock()
        updated_task = sample_task.model_copy()
        updated_task.status = TaskStatus.IN_PROGRESS
        mock_service.get_task.return_value = sample_task
        mock_service.update_task.return_value = updated_task
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await update_task_status(
            task_id="test_task_001",
            status="in_progress"
        )
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["id"] == sample_task.id
        assert result["data"]["status"] == "in_progress"
        assert "message" in result
        
        # Verify service calls
        mock_service.get_task.assert_called_once_with("test_task_001")
        mock_service.update_task.assert_called_once_with("test_task_001", status=TaskStatus.IN_PROGRESS)
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_update_task_status_not_found(self, mock_get_service):
        """Test updating status of non-existent task."""
        # Setup mock to return None
        mock_service = AsyncMock()
        mock_service.get_task.return_value = None
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await update_task_status(task_id="nonexistent", status="completed")
        
        # Verify error response
        assert result["success"] is False
        assert "Task not found" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_update_task_status_invalid_transition(self, mock_get_service, completed_task):
        """Test invalid status transition."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.get_task.return_value = completed_task
        mock_get_service.return_value = mock_service
        
        # Call tool with invalid transition (completed -> blocked is not typically valid)
        result = await update_task_status(
            task_id="test_task_003",
            status="blocked"
        )
        
        # Verify error response
        assert result["success"] is False
        assert "Invalid status transition" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_update_task_status_validation_error(self, mock_get_service):
        """Test task status update with validation error."""
        # Call tool with invalid status
        result = await update_task_status(
            task_id="test_task_001",
            status="invalid_status"
        )
        
        # Verify error response
        assert result["success"] is False
        assert "Validation error" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_update_task_status_service_error(self, mock_get_service, sample_task):
        """Test task status update with service error."""
        # Setup mock to raise error
        mock_service = AsyncMock()
        mock_service.get_task.return_value = sample_task
        mock_service.update_task.side_effect = TaskServiceError("Service error")
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await update_task_status(task_id="test_task_001", status="completed")
        
        # Verify error response
        assert result["success"] is False
        assert "Task service error" in result["error"]


class TestBulkStatusUpdate:
    """Test bulk_status_update tool."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_bulk_status_update_success(self, mock_get_service, sample_task, in_progress_task):
        """Test successful bulk status update."""
        # Setup mock
        mock_service = AsyncMock()
        
        # Mock get_task to return different tasks
        def mock_get_task(task_id):
            if task_id == "test_task_001":
                return sample_task
            elif task_id == "test_task_002":
                return in_progress_task
            return None
        
        mock_service.get_task.side_effect = mock_get_task
        
        # Mock update_task to return updated tasks
        updated_task1 = sample_task.model_copy()
        updated_task1.status = TaskStatus.COMPLETED
        updated_task2 = in_progress_task.model_copy()
        updated_task2.status = TaskStatus.COMPLETED
        
        def mock_update_task(task_id, **kwargs):
            if task_id == "test_task_001":
                return updated_task1
            elif task_id == "test_task_002":
                return updated_task2
            return None
        
        mock_service.update_task.side_effect = mock_update_task
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await bulk_status_update(
            task_ids=["test_task_001", "test_task_002"],
            status="completed"
        )
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["success_count"] == 2
        assert result["data"]["failure_count"] == 0
        assert result["data"]["total_processed"] == 2
        assert "test_task_001" in result["data"]["successful_updates"]
        assert "test_task_002" in result["data"]["successful_updates"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_bulk_status_update_partial_failure(self, mock_get_service, sample_task):
        """Test bulk status update with partial failures."""
        # Setup mock
        mock_service = AsyncMock()
        
        def mock_get_task(task_id):
            if task_id == "test_task_001":
                return sample_task
            return None  # Simulate task not found
        
        mock_service.get_task.side_effect = mock_get_task
        
        updated_task = sample_task.model_copy()
        updated_task.status = TaskStatus.COMPLETED
        mock_service.update_task.return_value = updated_task
        mock_get_service.return_value = mock_service
        
        # Call tool with one valid and one invalid task ID
        result = await bulk_status_update(
            task_ids=["test_task_001", "nonexistent"],
            status="completed"
        )
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["success_count"] == 1
        assert result["data"]["failure_count"] == 1
        assert result["data"]["total_processed"] == 2
        assert "test_task_001" in result["data"]["successful_updates"]
        assert len(result["data"]["failed_updates"]) == 1
        assert result["data"]["failed_updates"][0]["task_id"] == "nonexistent"
        assert "Task not found" in result["data"]["failed_updates"][0]["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_bulk_status_update_validation_error(self, mock_get_service):
        """Test bulk status update with validation error."""
        # Call tool with invalid status
        result = await bulk_status_update(
            task_ids=["test_task_001"],
            status="invalid_status"
        )
        
        # Verify error response
        assert result["success"] is False
        assert "Validation error" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_bulk_status_update_empty_list(self, mock_get_service):
        """Test bulk status update with empty task list."""
        # Call tool with empty list
        result = await bulk_status_update(
            task_ids=[],
            status="completed"
        )
        
        # Verify error response
        assert result["success"] is False
        assert "Validation error" in result["error"]


class TestGetTaskStatus:
    """Test get_task_status tool."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_get_task_status_success(self, mock_get_service, sample_task):
        """Test successful task status retrieval."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.get_task.return_value = sample_task
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await get_task_status(task_id="test_task_001")
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["task_id"] == sample_task.id
        assert result["data"]["current_status"] == sample_task.status.value
        assert "valid_transitions" in result["data"]
        assert "status_description" in result["data"]
        
        # Verify service call
        mock_service.get_task.assert_called_once_with("test_task_001")
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_get_task_status_not_found(self, mock_get_service):
        """Test getting status of non-existent task."""
        # Setup mock to return None
        mock_service = AsyncMock()
        mock_service.get_task.return_value = None
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await get_task_status(task_id="nonexistent")
        
        # Verify error response
        assert result["success"] is False
        assert "Task not found" in result["error"]


class TestGetTasksByStatus:
    """Test status-specific task retrieval tools."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_get_pending_tasks_success(self, mock_get_service, sample_task):
        """Test successful pending tasks retrieval."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.get_tasks_by_status.return_value = [sample_task]
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await get_pending_tasks()
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["total_count"] == 1
        assert result["data"]["status_filter"] == "pending"
        assert len(result["data"]["tasks"]) == 1
        assert result["data"]["tasks"][0]["id"] == sample_task.id
        assert result["data"]["tasks"][0]["status"] == "pending"
        
        # Verify service call
        mock_service.get_tasks_by_status.assert_called_once_with(TaskStatus.PENDING)
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_get_in_progress_tasks_success(self, mock_get_service, in_progress_task):
        """Test successful in-progress tasks retrieval."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.get_tasks_by_status.return_value = [in_progress_task]
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await get_in_progress_tasks()
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["total_count"] == 1
        assert result["data"]["status_filter"] == "in_progress"
        assert len(result["data"]["tasks"]) == 1
        assert result["data"]["tasks"][0]["id"] == in_progress_task.id
        assert result["data"]["tasks"][0]["status"] == "in_progress"
        
        # Verify service call
        mock_service.get_tasks_by_status.assert_called_once_with(TaskStatus.IN_PROGRESS)
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_get_blocked_tasks_success(self, mock_get_service, blocked_task):
        """Test successful blocked tasks retrieval."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.get_tasks_by_status.return_value = [blocked_task]
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await get_blocked_tasks()
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["total_count"] == 1
        assert result["data"]["status_filter"] == "blocked"
        assert len(result["data"]["tasks"]) == 1
        assert result["data"]["tasks"][0]["id"] == blocked_task.id
        assert result["data"]["tasks"][0]["status"] == "blocked"
        
        # Verify service call
        mock_service.get_tasks_by_status.assert_called_once_with(TaskStatus.BLOCKED)
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_get_completed_tasks_success(self, mock_get_service, completed_task):
        """Test successful completed tasks retrieval."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.get_tasks_by_status.return_value = [completed_task]
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await get_completed_tasks()
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["total_count"] == 1
        assert result["data"]["status_filter"] == "completed"
        assert len(result["data"]["tasks"]) == 1
        assert result["data"]["tasks"][0]["id"] == completed_task.id
        assert result["data"]["tasks"][0]["status"] == "completed"
        
        # Verify service call
        mock_service.get_tasks_by_status.assert_called_once_with(TaskStatus.COMPLETED)
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_get_pending_tasks_empty(self, mock_get_service):
        """Test pending tasks retrieval with no tasks."""
        # Setup mock to return empty list
        mock_service = AsyncMock()
        mock_service.get_tasks_by_status.return_value = []
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await get_pending_tasks()
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["total_count"] == 0
        assert len(result["data"]["tasks"]) == 0
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_get_tasks_by_status_multiple(self, mock_get_service, sample_task, blocked_task):
        """Test retrieving multiple tasks of the same status."""
        # Create another pending task
        pending_task2 = sample_task.model_copy()
        pending_task2.id = "test_task_005"
        pending_task2.title = "Another Pending Task"
        
        # Setup mock
        mock_service = AsyncMock()
        mock_service.get_tasks_by_status.return_value = [sample_task, pending_task2]
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await get_pending_tasks()
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["total_count"] == 2
        assert len(result["data"]["tasks"]) == 2
        
        # Verify both tasks are returned
        task_ids = [task["id"] for task in result["data"]["tasks"]]
        assert "test_task_001" in task_ids
        assert "test_task_005" in task_ids
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_get_tasks_service_error(self, mock_get_service):
        """Test task retrieval with service error."""
        # Setup mock to raise error
        mock_service = AsyncMock()
        mock_service.get_tasks_by_status.side_effect = TaskServiceError("Service error")
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await get_pending_tasks()
        
        # Verify error response
        assert result["success"] is False
        assert "error" in result


class TestStatusToolsIntegration:
    """Integration tests for status tools."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.status_tools._get_task_service')
    async def test_status_workflow(self, mock_get_service, sample_task):
        """Test complete status workflow: pending -> in_progress -> completed."""
        # Setup mock service
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        # Step 1: Get initial status (pending)
        mock_service.get_task.return_value = sample_task
        result = await get_task_status(task_id="test_task_001")
        assert result["success"] is True
        assert result["data"]["current_status"] == "pending"
        
        # Step 2: Update to in_progress
        in_progress_task = sample_task.model_copy()
        in_progress_task.status = TaskStatus.IN_PROGRESS
        mock_service.get_task.return_value = sample_task  # Current task
        mock_service.update_task.return_value = in_progress_task  # Updated task
        
        result = await update_task_status(task_id="test_task_001", status="in_progress")
        assert result["success"] is True
        assert result["data"]["status"] == "in_progress"
        
        # Step 3: Update to completed
        completed_task = in_progress_task.model_copy()
        completed_task.status = TaskStatus.COMPLETED
        mock_service.get_task.return_value = in_progress_task  # Current task
        mock_service.update_task.return_value = completed_task  # Updated task
        
        result = await update_task_status(task_id="test_task_001", status="completed")
        assert result["success"] is True
        assert result["data"]["status"] == "completed"
        
        # Step 4: Verify task appears in completed tasks
        mock_service.get_tasks_by_status.return_value = [completed_task]
        result = await get_completed_tasks()
        assert result["success"] is True
        assert result["data"]["total_count"] == 1
        assert result["data"]["tasks"][0]["id"] == "test_task_001"
        assert result["data"]["tasks"][0]["status"] == "completed"