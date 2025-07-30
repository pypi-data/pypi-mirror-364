"""
Simple tests for status management MCP tools.

This module tests the basic functionality of status tools
without complex mocking of private functions.
"""

import pytest
from datetime import datetime, timezone, timedelta

from src.todo_mcp.tools.status_tools import (
    update_task_status,
    bulk_status_update,
    get_task_status,
    get_pending_tasks,
    get_in_progress_tasks,
    get_blocked_tasks,
    get_completed_tasks,
)


class TestStatusToolsBasic:
    """Basic tests for status tools."""
    
    @pytest.mark.asyncio
    async def test_update_task_status_validation_error(self):
        """Test task status update with validation error."""
        # Call tool with invalid status
        result = await update_task_status(
            task_id="test_task_001",
            status="invalid_status"
        )
        
        # Verify error response
        assert result["success"] is False
        assert "error" in result
        assert "Validation error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_update_task_status_empty_task_id(self):
        """Test task status update with empty task ID."""
        # Call tool with empty task ID
        result = await update_task_status(
            task_id="",
            status="completed"
        )
        
        # Verify error response
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_bulk_status_update_validation_error(self):
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
    async def test_bulk_status_update_empty_list(self):
        """Test bulk status update with empty task list."""
        # Call tool with empty list
        result = await bulk_status_update(
            task_ids=[],
            status="completed"
        )
        
        # Verify error response
        assert result["success"] is False
        assert "Validation error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_task_status_empty_id(self):
        """Test getting status with empty task ID."""
        # Call tool with empty task ID
        result = await get_task_status(task_id="")
        
        # Verify error response
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_get_pending_tasks_structure(self):
        """Test that get_pending_tasks returns proper structure."""
        # Call tool
        result = await get_pending_tasks()
        
        # Verify response structure (should work even if no tasks exist)
        assert "success" in result
        assert "data" in result or "error" in result
        
        if result["success"]:
            assert "tasks" in result["data"]
            assert "total_count" in result["data"]
            assert "status_filter" in result["data"]
            assert result["data"]["status_filter"] == "pending"
    
    @pytest.mark.asyncio
    async def test_get_in_progress_tasks_structure(self):
        """Test that get_in_progress_tasks returns proper structure."""
        # Call tool
        result = await get_in_progress_tasks()
        
        # Verify response structure
        assert "success" in result
        assert "data" in result or "error" in result
        
        if result["success"]:
            assert "tasks" in result["data"]
            assert "total_count" in result["data"]
            assert "status_filter" in result["data"]
            assert result["data"]["status_filter"] == "in_progress"
    
    @pytest.mark.asyncio
    async def test_get_blocked_tasks_structure(self):
        """Test that get_blocked_tasks returns proper structure."""
        # Call tool
        result = await get_blocked_tasks()
        
        # Verify response structure
        assert "success" in result
        assert "data" in result or "error" in result
        
        if result["success"]:
            assert "tasks" in result["data"]
            assert "total_count" in result["data"]
            assert "status_filter" in result["data"]
            assert result["data"]["status_filter"] == "blocked"
    
    @pytest.mark.asyncio
    async def test_get_completed_tasks_structure(self):
        """Test that get_completed_tasks returns proper structure."""
        # Call tool
        result = await get_completed_tasks()
        
        # Verify response structure
        assert "success" in result
        assert "data" in result or "error" in result
        
        if result["success"]:
            assert "tasks" in result["data"]
            assert "total_count" in result["data"]
            assert "status_filter" in result["data"]
            assert result["data"]["status_filter"] == "completed"


class TestStatusToolsValidation:
    """Test Pydantic validation in status tools."""
    
    @pytest.mark.asyncio
    async def test_valid_status_values(self):
        """Test that valid status values are accepted."""
        valid_statuses = ["pending", "in_progress", "completed", "blocked"]
        
        for status in valid_statuses:
            result = await update_task_status(
                task_id="nonexistent_task",  # Will fail at service level, not validation
                status=status
            )
            
            # Should not fail at validation level
            if not result["success"]:
                # If it fails, it should not be due to validation error for valid statuses
                assert "Validation error" not in result.get("error", "")
    
    @pytest.mark.asyncio
    async def test_invalid_status_values(self):
        """Test that invalid status values are rejected."""
        invalid_statuses = ["invalid", "unknown", "draft", ""]
        
        for status in invalid_statuses:
            result = await update_task_status(
                task_id="test_task",
                status=status
            )
            
            # Should fail at validation level
            assert result["success"] is False
            assert "Validation error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_bulk_update_validation(self):
        """Test bulk update validation."""
        # Test with valid data structure
        result = await bulk_status_update(
            task_ids=["task1", "task2"],
            status="completed"
        )
        
        # Should not fail at validation level (may fail at service level)
        if not result["success"]:
            assert "Validation error" not in result.get("error", "")
        
        # Test with invalid status
        result = await bulk_status_update(
            task_ids=["task1"],
            status="invalid_status"
        )
        
        # Should fail at validation level
        assert result["success"] is False
        assert "Validation error" in result["error"]


class TestStatusToolsResponseFormat:
    """Test response format consistency."""
    
    @pytest.mark.asyncio
    async def test_error_response_format(self):
        """Test that error responses have consistent format."""
        # Generate an error response
        result = await update_task_status(
            task_id="test",
            status="invalid"
        )
        
        # Verify error response format
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is False
        assert "error" in result
        assert isinstance(result["error"], str)
        assert len(result["error"]) > 0
    
    @pytest.mark.asyncio
    async def test_task_list_response_format(self):
        """Test that task list responses have consistent format."""
        # Test all status-specific list functions
        list_functions = [
            get_pending_tasks,
            get_in_progress_tasks,
            get_blocked_tasks,
            get_completed_tasks
        ]
        
        for func in list_functions:
            result = await func()
            
            # Verify response structure
            assert isinstance(result, dict)
            assert "success" in result
            
            if result["success"]:
                assert "data" in result
                data = result["data"]
                assert "tasks" in data
                assert "total_count" in data
                assert "status_filter" in data
                assert isinstance(data["tasks"], list)
                assert isinstance(data["total_count"], int)
                assert isinstance(data["status_filter"], str)
                
                # If there are tasks, verify their structure
                for task in data["tasks"]:
                    assert "id" in task
                    assert "title" in task
                    assert "status" in task
                    assert "priority" in task
                    assert "tags" in task
                    assert isinstance(task["tags"], list)