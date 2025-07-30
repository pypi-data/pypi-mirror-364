"""
Tests for query tools module.

This module tests the MCP query tools for searching, filtering,
and getting statistics about tasks with Pydantic validation.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.todo_mcp.tools.query_tools import (
    search_tasks,
    filter_tasks,
    get_task_statistics,
    SearchTasksRequest,
    FilterTasksRequest,
    TaskStatisticsResponse,
    _task_to_response,
    _parse_status_list,
    _parse_priority_list,
    _parse_datetime,
    _search_result_to_response
)
from src.todo_mcp.models.task import Task
from src.todo_mcp.models.status import TaskStatus, Priority
from src.todo_mcp.models.filters import TaskFilter, TaskSearchResult


class TestPydanticModels:
    """Test Pydantic model validation."""
    
    def test_search_tasks_request_validation(self):
        """Test SearchTasksRequest validation."""
        # Valid request
        request = SearchTasksRequest(search_text="test query")
        assert request.search_text == "test query"
        assert request.include_completed is True
        assert request.offset == 0
        
        # Test with all fields
        request = SearchTasksRequest(
            search_text="test",
            search_fields=["title", "description"],
            status=["pending", "in_progress"],
            priority=["high"],
            tags=["urgent"],
            include_completed=False,
            limit=50,
            offset=10
        )
        assert request.search_fields == ["title", "description"]
        assert request.status == ["pending", "in_progress"]
        assert request.limit == 50
        
        # Test validation errors
        with pytest.raises(Exception):  # Empty search text
            SearchTasksRequest(search_text="")
        
        with pytest.raises(Exception):  # Invalid limit
            SearchTasksRequest(search_text="test", limit=0)
        
        with pytest.raises(Exception):  # Invalid offset
            SearchTasksRequest(search_text="test", offset=-1)
    
    def test_filter_tasks_request_validation(self):
        """Test FilterTasksRequest validation."""
        # Valid minimal request
        request = FilterTasksRequest()
        assert request.include_completed is True
        assert request.offset == 0
        assert request.sort_by == "created_at"
        assert request.sort_desc is True
        
        # Test with all fields
        request = FilterTasksRequest(
            status=["pending"],
            priority=["high"],
            tags=["work"],
            tags_all=["urgent", "important"],
            parent_id="parent-123",
            has_parent=True,
            has_children=False,
            has_due_date=True,
            created_after="2024-01-01T00:00:00Z",
            title_contains="test",
            limit=100,
            sort_by="title",
            sort_desc=False
        )
        assert request.status == ["pending"]
        assert request.tags_all == ["urgent", "important"]
        assert request.created_after == "2024-01-01T00:00:00Z"
        assert request.sort_by == "title"
        
        # Test validation errors
        with pytest.raises(Exception):  # Invalid limit
            FilterTasksRequest(limit=2000)
        
        with pytest.raises(Exception):  # Invalid offset
            FilterTasksRequest(offset=-5)
    
    def test_task_statistics_response_validation(self):
        """Test TaskStatisticsResponse validation."""
        # Valid response
        response = TaskStatisticsResponse(
            total_tasks=100,
            by_status={"pending": 50, "completed": 50},
            by_priority={"high": 25, "medium": 75},
            with_due_dates=30,
            overdue=5,
            created_today=10,
            updated_today=15,
            completed_today=8
        )
        assert response.total_tasks == 100
        assert response.by_status["pending"] == 50
        assert response.overdue == 5


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_parse_status_list(self):
        """Test status list parsing."""
        # Valid statuses
        statuses = _parse_status_list(["pending", "in_progress", "completed"])
        assert len(statuses) == 3
        assert TaskStatus.PENDING in statuses
        assert TaskStatus.IN_PROGRESS in statuses
        assert TaskStatus.COMPLETED in statuses
        
        # Invalid status should raise ValidationError
        with pytest.raises(Exception):
            _parse_status_list(["invalid_status"])
    
    def test_parse_priority_list(self):
        """Test priority list parsing."""
        # Valid priorities
        priorities = _parse_priority_list(["low", "medium", "high", "urgent"])
        assert len(priorities) == 4
        assert Priority.LOW in priorities
        assert Priority.MEDIUM in priorities
        assert Priority.HIGH in priorities
        assert Priority.URGENT in priorities
        
        # Invalid priority should raise ValidationError
        with pytest.raises(Exception):
            _parse_priority_list(["invalid_priority"])
    
    def test_parse_datetime(self):
        """Test datetime parsing."""
        # Valid ISO datetime
        dt = _parse_datetime("2024-01-20T17:00:00Z")
        assert isinstance(dt, datetime)
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 20
        
        # Valid datetime without Z
        dt = _parse_datetime("2024-01-20T17:00:00+00:00")
        assert isinstance(dt, datetime)
        
        # Invalid datetime should raise ValidationError
        with pytest.raises(Exception):
            _parse_datetime("invalid-date")
    
    def test_task_to_response(self):
        """Test task to response conversion."""
        # Create test task with future dates
        now = datetime.utcnow()
        future_date = now + timedelta(days=5)
        
        task = Task(
            id="test-123",
            title="Test Task",
            description="Test description",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            tags=["work", "urgent"],
            parent_id="parent-123",
            child_ids=["child-1", "child-2"],
            created_at=now,
            updated_at=now,
            due_date=future_date,
            tool_calls=[],
            metadata={"key": "value"}
        )
        
        response = _task_to_response(task)
        assert response.id == "test-123"
        assert response.title == "Test Task"
        assert response.status == "pending"
        assert response.priority == "high"
        assert response.tags == ["work", "urgent"]
        assert response.parent_id == "parent-123"
        assert response.child_ids == ["child-1", "child-2"]
        assert response.created_at == now.isoformat()
        assert response.due_date == future_date.isoformat()
        assert response.metadata == {"key": "value"}
    
    def test_search_result_to_response(self):
        """Test search result to response conversion."""
        # Create test task with current time
        now = datetime.utcnow()
        
        task = Task(
            id="test-123",
            title="Test Task",
            description="Test description",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            tags=["work"],
            parent_id=None,
            child_ids=[],
            created_at=now,
            updated_at=now,
            due_date=None,
            tool_calls=[],
            metadata={}
        )
        
        # Create test filter
        task_filter = TaskFilter(search_text="test")
        
        # Create test search result
        search_result = TaskSearchResult(
            tasks=[task],
            total_count=1,
            filtered_count=1,
            has_more=False,
            offset=0,
            limit=None,
            filter_applied=task_filter,
            search_time_ms=50.0
        )
        
        response = _search_result_to_response(search_result)
        assert len(response.tasks) == 1
        assert response.total_count == 1
        assert response.filtered_count == 1
        assert response.has_more is False
        assert response.search_time_ms == 50.0


class TestSearchTasks:
    """Test search_tasks function."""
    
    @pytest.fixture
    def mock_task_service(self):
        """Mock task service."""
        service = AsyncMock()
        return service
    
    @pytest.fixture
    def sample_task(self):
        """Sample task for testing."""
        now = datetime.utcnow()
        return Task(
            id="test-123",
            title="Test Task",
            description="Test description",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            tags=["work"],
            parent_id=None,
            child_ids=[],
            created_at=now,
            updated_at=now,
            due_date=None,
            tool_calls=[],
            metadata={}
        )
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.query_tools._get_task_service')
    async def test_search_tasks_success(self, mock_get_service, mock_task_service, sample_task):
        """Test successful task search."""
        # Setup mock
        mock_get_service.return_value = mock_task_service
        
        # Create mock search result
        task_filter = TaskFilter(search_text="test")
        search_result = TaskSearchResult(
            tasks=[sample_task],
            total_count=1,
            filtered_count=1,
            has_more=False,
            offset=0,
            limit=None,
            filter_applied=task_filter,
            search_time_ms=25.0
        )
        mock_task_service.filter_tasks.return_value = search_result
        
        # Call function
        result = await search_tasks(
            search_text="test query",
            status=["pending"],
            priority=["high"],
            limit=50
        )
        
        # Verify result
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["total_count"] == 1
        assert len(result["data"]["tasks"]) == 1
        assert result["data"]["tasks"][0]["title"] == "Test Task"
        
        # Verify service was called correctly
        mock_task_service.filter_tasks.assert_called_once()
        call_args = mock_task_service.filter_tasks.call_args[0][0]
        assert call_args.search_text == "test query"
        assert TaskStatus.PENDING in call_args.status
        assert Priority.HIGH in call_args.priority
        assert call_args.limit == 50
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.query_tools._get_task_service')
    async def test_search_tasks_validation_error(self, mock_get_service):
        """Test search with validation error."""
        # Call with invalid parameters
        result = await search_tasks(
            search_text="",  # Empty search text should fail validation
        )
        
        # Verify error response
        assert result["success"] is False
        assert "error" in result
        assert "Validation error" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.query_tools._get_task_service')
    async def test_search_tasks_service_error(self, mock_get_service, mock_task_service):
        """Test search with service error."""
        # Setup mock to raise error
        mock_get_service.return_value = mock_task_service
        mock_task_service.filter_tasks.side_effect = Exception("Service error")
        
        # Call function
        result = await search_tasks(search_text="test")
        
        # Verify error response
        assert result["success"] is False
        assert "error" in result
        assert "Unexpected error" in result["error"]


class TestFilterTasks:
    """Test filter_tasks function."""
    
    @pytest.fixture
    def mock_task_service(self):
        """Mock task service."""
        service = AsyncMock()
        return service
    
    @pytest.fixture
    def sample_tasks(self):
        """Sample tasks for testing."""
        now = datetime.utcnow()
        future_date = now + timedelta(days=5)
        past_date = now - timedelta(hours=1)
        
        return [
            Task(
                id="task-1",
                title="Task 1",
                description="First task",
                status=TaskStatus.PENDING,
                priority=Priority.HIGH,
                tags=["work", "urgent"],
                parent_id=None,
                child_ids=[],
                created_at=past_date,
                updated_at=now,
                due_date=future_date,
                tool_calls=[],
                metadata={}
            ),
            Task(
                id="task-2",
                title="Task 2",
                description="Second task",
                status=TaskStatus.COMPLETED,
                priority=Priority.MEDIUM,
                tags=["personal"],
                parent_id="task-1",
                child_ids=[],
                created_at=past_date,
                updated_at=now,
                due_date=None,
                tool_calls=[],
                metadata={}
            )
        ]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.query_tools._get_task_service')
    async def test_filter_tasks_success(self, mock_get_service, mock_task_service, sample_tasks):
        """Test successful task filtering."""
        # Setup mock
        mock_get_service.return_value = mock_task_service
        
        # Create mock filter result
        task_filter = TaskFilter(status=[TaskStatus.PENDING])
        filter_result = TaskSearchResult(
            tasks=[sample_tasks[0]],  # Only pending task
            total_count=1,
            filtered_count=1,
            has_more=False,
            offset=0,
            limit=None,
            filter_applied=task_filter,
            search_time_ms=15.0
        )
        mock_task_service.filter_tasks.return_value = filter_result
        
        # Call function
        result = await filter_tasks(
            status=["pending"],
            priority=["high"],
            has_due_date=True,
            sort_by="title",
            sort_desc=False
        )
        
        # Verify result
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["total_count"] == 1
        assert len(result["data"]["tasks"]) == 1
        assert result["data"]["tasks"][0]["status"] == "pending"
        
        # Verify service was called correctly
        mock_task_service.filter_tasks.assert_called_once()
        call_args = mock_task_service.filter_tasks.call_args[0][0]
        assert TaskStatus.PENDING in call_args.status
        assert Priority.HIGH in call_args.priority
        assert call_args.has_due_date is True
        assert call_args.sort_by == "title"
        assert call_args.sort_desc is False
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.query_tools._get_task_service')
    async def test_filter_tasks_with_dates(self, mock_get_service, mock_task_service, sample_tasks):
        """Test filtering with date parameters."""
        # Setup mock
        mock_get_service.return_value = mock_task_service
        
        task_filter = TaskFilter()
        filter_result = TaskSearchResult(
            tasks=sample_tasks,
            total_count=2,
            filtered_count=2,
            has_more=False,
            offset=0,
            limit=None,
            filter_applied=task_filter,
            search_time_ms=20.0
        )
        mock_task_service.filter_tasks.return_value = filter_result
        
        # Call function with date filters (using future dates)
        now = datetime.utcnow()
        future_start = now + timedelta(days=1)
        future_end = now + timedelta(days=10)
        
        result = await filter_tasks(
            created_after=now.isoformat() + "Z",
            created_before=future_end.isoformat() + "Z",
            due_after=future_start.isoformat() + "Z",
            due_before=future_end.isoformat() + "Z"
        )
        
        # Verify result
        assert result["success"] is True
        
        # Verify service was called with parsed dates
        mock_task_service.filter_tasks.assert_called_once()
        call_args = mock_task_service.filter_tasks.call_args[0][0]
        assert call_args.created_after is not None
        assert call_args.created_before is not None
        assert call_args.due_after is not None
        assert call_args.due_before is not None
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.query_tools._get_task_service')
    async def test_filter_tasks_validation_error(self, mock_get_service):
        """Test filter with validation error."""
        # Call with invalid parameters
        result = await filter_tasks(
            limit=-1,  # Invalid limit
        )
        
        # Verify error response
        assert result["success"] is False
        assert "error" in result
        assert "Validation error" in result["error"]


class TestGetTaskStatistics:
    """Test get_task_statistics function."""
    
    @pytest.fixture
    def mock_task_service(self):
        """Mock task service."""
        service = AsyncMock()
        return service
    
    @pytest.fixture
    def sample_statistics(self):
        """Sample statistics data."""
        return {
            'total_tasks': 100,
            'by_status': {
                'pending': 30,
                'in_progress': 20,
                'completed': 45,
                'blocked': 5
            },
            'by_priority': {
                'low': 25,
                'medium': 50,
                'high': 20,
                'urgent': 5
            },
            'with_due_dates': 60,
            'overdue': 8,
            'created_today': 5,
            'updated_today': 12,
            'completed_today': 3
        }
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.query_tools._get_task_service')
    async def test_get_task_statistics_success(self, mock_get_service, mock_task_service, sample_statistics):
        """Test successful statistics retrieval."""
        # Setup mock
        mock_get_service.return_value = mock_task_service
        mock_task_service.get_task_statistics.return_value = sample_statistics
        
        # Call function
        result = await get_task_statistics()
        
        # Verify result
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["total_tasks"] == 100
        assert result["data"]["by_status"]["pending"] == 30
        assert result["data"]["by_priority"]["high"] == 20
        assert result["data"]["overdue"] == 8
        
        # Verify service was called
        mock_task_service.get_task_statistics.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.query_tools._get_task_service')
    async def test_get_task_statistics_service_error(self, mock_get_service, mock_task_service):
        """Test statistics with service error."""
        # Setup mock to return error
        mock_get_service.return_value = mock_task_service
        mock_task_service.get_task_statistics.return_value = {'error': 'Database error'}
        
        # Call function
        result = await get_task_statistics()
        
        # Verify error response
        assert result["success"] is False
        assert "error" in result
        assert "Failed to get statistics" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.query_tools._get_task_service')
    async def test_get_task_statistics_exception(self, mock_get_service, mock_task_service):
        """Test statistics with exception."""
        # Setup mock to raise exception
        mock_get_service.return_value = mock_task_service
        mock_task_service.get_task_statistics.side_effect = Exception("Service error")
        
        # Call function
        result = await get_task_statistics()
        
        # Verify error response
        assert result["success"] is False
        assert "error" in result
        assert "Unexpected error" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.query_tools._get_task_service')
    async def test_get_task_statistics_empty(self, mock_get_service, mock_task_service):
        """Test statistics with no tasks."""
        # Setup mock with empty statistics
        mock_get_service.return_value = mock_task_service
        empty_stats = {
            'total_tasks': 0,
            'by_status': {},
            'by_priority': {},
            'with_due_dates': 0,
            'overdue': 0,
            'created_today': 0,
            'updated_today': 0,
            'completed_today': 0
        }
        mock_task_service.get_task_statistics.return_value = empty_stats
        
        # Call function
        result = await get_task_statistics()
        
        # Verify result
        assert result["success"] is True
        assert result["data"]["total_tasks"] == 0
        assert result["data"]["by_status"] == {}
        assert result["data"]["overdue"] == 0


class TestIntegration:
    """Integration tests for query tools."""
    
    @pytest.mark.asyncio
    @patch('src.todo_mcp.tools.query_tools._get_task_service')
    async def test_search_and_filter_consistency(self, mock_get_service):
        """Test that search and filter produce consistent results."""
        # Setup mock service
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        # Create sample task
        now = datetime.utcnow()
        task = Task(
            id="test-123",
            title="Test Task",
            description="Test description",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            tags=["work"],
            parent_id=None,
            child_ids=[],
            created_at=now,
            updated_at=now,
            due_date=None,
            tool_calls=[],
            metadata={}
        )
        
        # Mock filter result
        task_filter = TaskFilter()
        filter_result = TaskSearchResult(
            tasks=[task],
            total_count=1,
            filtered_count=1,
            has_more=False,
            offset=0,
            limit=None,
            filter_applied=task_filter,
            search_time_ms=10.0
        )
        mock_service.filter_tasks.return_value = filter_result
        
        # Test search
        search_result = await search_tasks(search_text="test")
        
        # Test filter with same criteria
        filter_result_direct = await filter_tasks(title_contains="test")
        
        # Both should succeed and have similar structure
        assert search_result["success"] is True
        assert filter_result_direct["success"] is True
        assert search_result["data"]["total_count"] == filter_result_direct["data"]["total_count"]