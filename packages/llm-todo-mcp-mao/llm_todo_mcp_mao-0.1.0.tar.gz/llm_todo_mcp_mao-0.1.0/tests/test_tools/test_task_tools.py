"""
Tests for task management MCP tools.

This module tests the MCP tools for task CRUD operations,
including Pydantic validation and error handling.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.todo_mcp.tools.task_tools import (
    create_task,
    update_task,
    delete_task,
    get_task,
    list_tasks,
    get_task_context,
    _task_to_response,
    _parse_priority,
    _parse_status,
    _parse_datetime,
)
from src.todo_mcp.models.task import Task
from src.todo_mcp.models.status import TaskStatus, Priority
from src.todo_mcp.services.task_service import TaskServiceError, TaskNotFoundError, TaskValidationError


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    # Use future dates to avoid validation errors
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
def mock_task_service():
    """Create a mock task service."""
    service = AsyncMock()
    return service


class TestTaskToolsHelpers:
    """Test helper functions."""
    
    def test_task_to_response(self, sample_task):
        """Test task to response conversion."""
        response = _task_to_response(sample_task)
        
        assert response.id == sample_task.id
        assert response.title == sample_task.title
        assert response.description == sample_task.description
        assert response.status == sample_task.status.value
        assert response.priority == sample_task.priority.name.lower()
        assert response.tags == sample_task.tags
        assert response.parent_id == sample_task.parent_id
        assert response.child_ids == sample_task.child_ids
        assert response.created_at == sample_task.created_at.isoformat()
        assert response.updated_at == sample_task.updated_at.isoformat()
        assert response.due_date == sample_task.due_date.isoformat()
        assert response.metadata == sample_task.metadata
    
    def test_parse_priority_valid(self):
        """Test parsing valid priority strings."""
        assert _parse_priority("low") == Priority.LOW
        assert _parse_priority("medium") == Priority.MEDIUM
        assert _parse_priority("high") == Priority.HIGH
        assert _parse_priority("urgent") == Priority.URGENT
        assert _parse_priority("LOW") == Priority.LOW
        assert _parse_priority("Medium") == Priority.MEDIUM
    
    def test_parse_priority_invalid(self):
        """Test parsing invalid priority strings."""
        with pytest.raises(Exception):  # ValidationError
            _parse_priority("invalid")
        
        with pytest.raises(Exception):
            _parse_priority("")
    
    def test_parse_status_valid(self):
        """Test parsing valid status strings."""
        assert _parse_status("pending") == TaskStatus.PENDING
        assert _parse_status("in_progress") == TaskStatus.IN_PROGRESS
        assert _parse_status("completed") == TaskStatus.COMPLETED
        assert _parse_status("blocked") == TaskStatus.BLOCKED
        assert _parse_status("PENDING") == TaskStatus.PENDING
    
    def test_parse_status_invalid(self):
        """Test parsing invalid status strings."""
        with pytest.raises(Exception):  # ValidationError
            _parse_status("invalid")
        
        with pytest.raises(Exception):
            _parse_status("")
    
    def test_parse_datetime_valid(self):
        """Test parsing valid datetime strings."""
        dt = _parse_datetime("2024-01-20T17:00:00Z")
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 20
        assert dt.hour == 17
        
        dt2 = _parse_datetime("2024-01-20T17:00:00+00:00")
        assert dt2.year == 2024
    
    def test_parse_datetime_invalid(self):
        """Test parsing invalid datetime strings."""
        with pytest.raises(Exception):  # ValidationError
            _parse_datetime("invalid")
        
        with pytest.raises(Exception):
            _parse_datetime("2024-13-01")


class TestCreateTask:
    """Test create_task tool."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_create_task_success(self, mock_get_service, sample_task):
        """Test successful task creation."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.create_task.return_value = sample_task
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await create_task(
            title="Test Task",
            description="Test description",
            priority="medium",
            tags=["test"],
            parent_id=None
        )
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["id"] == sample_task.id
        assert result["data"]["title"] == sample_task.title
        assert "message" in result
        
        # Verify service call
        mock_service.create_task.assert_called_once()
        call_args = mock_service.create_task.call_args
        assert call_args.kwargs["title"] == "Test Task"
        assert call_args.kwargs["description"] == "Test description"
        assert call_args.kwargs["priority"] == Priority.MEDIUM
        assert call_args.kwargs["tags"] == ["test"]
    
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    @pytest.mark.asyncio
    async def test_create_task_validation_error(self, mock_get_service):
        """Test task creation with validation error."""
        # Call tool with invalid data
        result = await create_task(
            title="",  # Invalid empty title
            description="Test description"
        )
        
        # Verify error response
        assert result["success"] is False
        assert "error" in result
        assert "Validation error" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_create_task_service_error(self, mock_get_service):
        """Test task creation with service error."""
        # Setup mock to raise error
        mock_service = AsyncMock()
        mock_service.create_task.side_effect = TaskServiceError("Service error")
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await create_task(title="Test Task")
        
        # Verify error response
        assert result["success"] is False
        assert "error" in result
        assert "Task service error" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_create_task_with_due_date(self, mock_get_service, sample_task):
        """Test task creation with due date."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.create_task.return_value = sample_task
        mock_get_service.return_value = mock_service
        
        # Call tool with due date (use future date)
        future_date = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
        result = await create_task(
            title="Test Task",
            due_date=future_date
        )
        
        # Verify result
        assert result["success"] is True
        
        # Verify service was called with parsed due date
        mock_service.create_task.assert_called_once()
        call_args = mock_service.create_task.call_args
        assert call_args.kwargs["due_date"] is not None
        assert call_args.kwargs["due_date"] > datetime.now(timezone.utc)


class TestUpdateTask:
    """Test update_task tool."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_update_task_success(self, mock_get_service, sample_task):
        """Test successful task update."""
        # Setup mock
        mock_service = AsyncMock()
        updated_task = sample_task.model_copy()
        updated_task.title = "Updated Title"
        mock_service.update_task.return_value = updated_task
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await update_task(
            task_id="test_task_001",
            title="Updated Title",
            priority="high"
        )
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["title"] == "Updated Title"
        
        # Verify service call
        mock_service.update_task.assert_called_once()
        call_args = mock_service.update_task.call_args
        assert call_args.args[0] == "test_task_001"
        assert call_args.kwargs["title"] == "Updated Title"
        assert call_args.kwargs["priority"] == Priority.HIGH
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_update_task_not_found(self, mock_get_service):
        """Test updating non-existent task."""
        # Setup mock to return None
        mock_service = AsyncMock()
        mock_service.update_task.return_value = None
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await update_task(task_id="nonexistent", title="New Title")
        
        # Verify error response
        assert result["success"] is False
        assert "Task not found" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_update_task_validation_error(self, mock_get_service):
        """Test task update with validation error."""
        # Call tool with invalid data
        result = await update_task(
            task_id="test_task_001",
            title="",  # Invalid empty title
        )
        
        # Verify error response
        assert result["success"] is False
        assert "Validation error" in result["error"]


class TestDeleteTask:
    """Test delete_task tool."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_delete_task_success(self, mock_get_service):
        """Test successful task deletion."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.delete_task.return_value = True
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await delete_task(task_id="test_task_001")
        
        # Verify result
        assert result["success"] is True
        assert "deleted successfully" in result["message"]
        
        # Verify service call
        mock_service.delete_task.assert_called_once_with("test_task_001", cascade=False)
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_delete_task_not_found(self, mock_get_service):
        """Test deleting non-existent task."""
        # Setup mock to return False
        mock_service = AsyncMock()
        mock_service.delete_task.return_value = False
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await delete_task(task_id="nonexistent")
        
        # Verify error response
        assert result["success"] is False
        assert "Task not found" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_delete_task_cascade(self, mock_get_service):
        """Test task deletion with cascade."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.delete_task.return_value = True
        mock_get_service.return_value = mock_service
        
        # Call tool with cascade
        result = await delete_task(task_id="test_task_001", cascade=True)
        
        # Verify result
        assert result["success"] is True
        
        # Verify service call with cascade
        mock_service.delete_task.assert_called_once_with("test_task_001", cascade=True)


class TestGetTask:
    """Test get_task tool."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_get_task_success(self, mock_get_service, sample_task):
        """Test successful task retrieval."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.get_task.return_value = sample_task
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await get_task(task_id="test_task_001")
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["id"] == sample_task.id
        assert result["data"]["title"] == sample_task.title
        
        # Verify service call
        mock_service.get_task.assert_called_once_with("test_task_001")
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_get_task_not_found(self, mock_get_service):
        """Test getting non-existent task."""
        # Setup mock to return None
        mock_service = AsyncMock()
        mock_service.get_task.return_value = None
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await get_task(task_id="nonexistent")
        
        # Verify error response
        assert result["success"] is False
        assert "Task not found" in result["error"]


class TestListTasks:
    """Test list_tasks tool."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_list_tasks_success(self, mock_get_service, sample_task):
        """Test successful task listing."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.list_tasks.return_value = [sample_task]
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await list_tasks()
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["total_count"] == 1
        assert len(result["data"]["tasks"]) == 1
        assert result["data"]["tasks"][0]["id"] == sample_task.id
        
        # Verify service call
        mock_service.list_tasks.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_list_tasks_with_filters(self, mock_get_service, sample_task):
        """Test task listing with filters."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.list_tasks.return_value = [sample_task]
        mock_get_service.return_value = mock_service
        
        # Call tool with filters
        result = await list_tasks(
            status="pending",
            priority="medium",
            tags=["test"],
            parent_id="parent_001",
            include_completed=False
        )
        
        # Verify result
        assert result["success"] is True
        
        # Verify service call with filters
        mock_service.list_tasks.assert_called_once()
        call_args = mock_service.list_tasks.call_args
        assert call_args.kwargs["status"] == TaskStatus.PENDING
        assert call_args.kwargs["priority"] == Priority.MEDIUM
        assert call_args.kwargs["tags"] == ["test"]
        assert call_args.kwargs["parent_id"] == "parent_001"
        assert call_args.kwargs["include_completed"] is False
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_list_tasks_empty(self, mock_get_service):
        """Test listing with no tasks."""
        # Setup mock to return empty list
        mock_service = AsyncMock()
        mock_service.list_tasks.return_value = []
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await list_tasks()
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["total_count"] == 0
        assert len(result["data"]["tasks"]) == 0


class TestGetTaskContext:
    """Test get_task_context tool."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_get_task_context_success(self, mock_get_service, sample_task):
        """Test successful task context retrieval."""
        # Create parent and child tasks
        parent_task = Task(
            id="parent_001",
            title="Parent Task",
            description="Parent description",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.HIGH,
            child_ids=[sample_task.id]
        )
        
        child_task = Task(
            id="child_001",
            title="Child Task",
            description="Child description",
            status=TaskStatus.PENDING,
            priority=Priority.LOW,
            parent_id=sample_task.id
        )
        
        # Setup mock
        mock_service = AsyncMock()
        mock_service.get_task.side_effect = lambda task_id: {
            sample_task.id: sample_task,
            "parent_001": parent_task,
            "child_001": child_task,
            "child_002": None  # Simulate missing child
        }.get(task_id)
        mock_get_service.return_value = mock_service
        
        # Update sample task to have parent
        sample_task.parent_id = "parent_001"
        
        # Call tool
        result = await get_task_context(task_id=sample_task.id)
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["task"]["id"] == sample_task.id
        assert result["data"]["parent"]["id"] == parent_task.id
        assert len(result["data"]["children"]) == 1  # Only one child found
        assert result["data"]["children"][0]["id"] == child_task.id
        assert result["data"]["total_descendants"] == 1
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_get_task_context_not_found(self, mock_get_service):
        """Test getting context for non-existent task."""
        # Setup mock to return None
        mock_service = AsyncMock()
        mock_service.get_task.return_value = None
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await get_task_context(task_id="nonexistent")
        
        # Verify error response
        assert result["success"] is False
        assert "Task not found" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.task_tools._get_task_service')
    async def test_get_task_context_no_relationships(self, mock_get_service, sample_task):
        """Test getting context for task with no parent or children."""
        # Remove relationships
        sample_task.parent_id = None
        sample_task.child_ids = []
        
        # Setup mock
        mock_service = AsyncMock()
        mock_service.get_task.return_value = sample_task
        mock_get_service.return_value = mock_service
        
        # Call tool
        result = await get_task_context(task_id=sample_task.id)
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["task"]["id"] == sample_task.id
        assert result["data"]["parent"] is None
        assert len(result["data"]["children"]) == 0
        assert result["data"]["total_descendants"] == 0