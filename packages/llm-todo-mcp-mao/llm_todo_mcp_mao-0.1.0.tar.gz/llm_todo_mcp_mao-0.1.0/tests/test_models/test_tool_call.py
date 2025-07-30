"""
Unit tests for the ToolCall model.

This module tests the ToolCall model validation, serialization,
and functionality.
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from src.todo_mcp.models.tool_call import ToolCall


class TestToolCall:
    """Test cases for the ToolCall model."""
    
    def test_tool_call_creation_minimal(self):
        """Test creating a tool call with minimal required fields."""
        tool_call = ToolCall(tool_name="create_task")
        
        assert tool_call.tool_name == "create_task"
        assert isinstance(tool_call.timestamp, datetime)
        assert tool_call.timestamp.tzinfo is not None  # Should be timezone-aware
        assert tool_call.parameters == {}
        assert tool_call.result is None
        assert tool_call.agent_id is None
        assert tool_call.success is True
        assert tool_call.error_message is None
        assert tool_call.duration_ms is None
    
    def test_tool_call_creation_full(self):
        """Test creating a tool call with all fields."""
        timestamp = datetime.now(timezone.utc)
        parameters = {"task_id": "test-001", "title": "Test Task"}
        result = {"success": True, "task_id": "test-001"}
        
        tool_call = ToolCall(
            timestamp=timestamp,
            tool_name="create_task",
            parameters=parameters,
            result=result,
            agent_id="agent-001",
            success=True,
            error_message=None,
            duration_ms=150
        )
        
        assert tool_call.timestamp == timestamp
        assert tool_call.tool_name == "create_task"
        assert tool_call.parameters == parameters
        assert tool_call.result == result
        assert tool_call.agent_id == "agent-001"
        assert tool_call.success is True
        assert tool_call.error_message is None
        assert tool_call.duration_ms == 150
    
    def test_tool_call_validation_empty_tool_name(self):
        """Test that empty tool name raises validation error."""
        with pytest.raises(ValidationError):
            ToolCall(tool_name="")
        
        with pytest.raises(ValidationError):
            ToolCall(tool_name="   ")
    
    def test_tool_call_validation_invalid_tool_name(self):
        """Test that invalid tool name characters raise validation error."""
        with pytest.raises(ValidationError):
            ToolCall(tool_name="create@task")
        
        with pytest.raises(ValidationError):
            ToolCall(tool_name="create task")
    
    def test_tool_call_validation_negative_duration(self):
        """Test that negative duration raises validation error."""
        with pytest.raises(ValidationError):
            ToolCall(tool_name="create_task", duration_ms=-100)
    
    def test_tool_call_timezone_handling(self):
        """Test that timestamps are properly handled with timezones."""
        # Test with timezone-naive datetime
        naive_time = datetime(2024, 1, 15, 10, 30, 0)
        tool_call = ToolCall(tool_name="create_task", timestamp=naive_time)
        
        # Should be converted to UTC
        assert tool_call.timestamp.tzinfo == timezone.utc
        assert tool_call.timestamp.replace(tzinfo=None) == naive_time
        
        # Test with timezone-aware datetime
        aware_time = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        tool_call2 = ToolCall(tool_name="create_task", timestamp=aware_time)
        
        # Should preserve the timezone
        assert tool_call2.timestamp == aware_time
    
    def test_tool_call_mark_success(self):
        """Test marking a tool call as successful."""
        tool_call = ToolCall(tool_name="create_task", success=False, error_message="Initial error")
        result = {"task_id": "test-001"}
        
        tool_call.mark_success(result=result, duration_ms=200)
        
        assert tool_call.success is True
        assert tool_call.error_message is None
        assert tool_call.result == result
        assert tool_call.duration_ms == 200
    
    def test_tool_call_mark_failure(self):
        """Test marking a tool call as failed."""
        tool_call = ToolCall(tool_name="create_task", success=True, result={"initial": "result"})
        error_msg = "Task creation failed"
        
        tool_call.mark_failure(error_message=error_msg, duration_ms=50)
        
        assert tool_call.success is False
        assert tool_call.error_message == error_msg
        assert tool_call.result is None
        assert tool_call.duration_ms == 50
    
    def test_tool_call_audit_string_success(self):
        """Test audit string generation for successful calls."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        tool_call = ToolCall(
            tool_name="create_task",
            timestamp=timestamp,
            agent_id="agent-001",
            success=True,
            duration_ms=150
        )
        
        audit_string = tool_call.to_audit_string()
        
        assert "SUCCESS" in audit_string
        assert "create_task" in audit_string
        assert "agent-001" in audit_string
        assert "150ms" in audit_string
        assert "2024-01-15T10:30:00+00:00" in audit_string
    
    def test_tool_call_audit_string_failure(self):
        """Test audit string generation for failed calls."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        tool_call = ToolCall(
            tool_name="create_task",
            timestamp=timestamp,
            agent_id="agent-001",
            success=False,
            error_message="Validation failed",
            duration_ms=75
        )
        
        audit_string = tool_call.to_audit_string()
        
        assert "FAILURE" in audit_string
        assert "create_task" in audit_string
        assert "agent-001" in audit_string
        assert "75ms" in audit_string
        assert "Validation failed" in audit_string
        assert "2024-01-15T10:30:00+00:00" in audit_string
    
    def test_tool_call_audit_string_minimal(self):
        """Test audit string generation with minimal information."""
        tool_call = ToolCall(tool_name="create_task")
        
        audit_string = tool_call.to_audit_string()
        
        assert "SUCCESS" in audit_string
        assert "create_task" in audit_string
        assert "agent" not in audit_string  # No agent ID
        assert "ms" not in audit_string     # No duration
    
    def test_tool_call_string_representation(self):
        """Test tool call string representations."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        tool_call = ToolCall(tool_name="create_task", timestamp=timestamp, success=True)
        
        str_repr = str(tool_call)
        assert "✓" in str_repr
        assert "create_task" in str_repr
        assert "2024-01-15T10:30:00+00:00" in str_repr
        
        # Test failed call
        tool_call.success = False
        str_repr = str(tool_call)
        assert "✗" in str_repr
    
    def test_tool_call_serialization(self):
        """Test tool call JSON serialization."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        tool_call = ToolCall(
            tool_name="create_task",
            timestamp=timestamp,
            parameters={"title": "Test"},
            success=True
        )
        
        # Test that tool call can be serialized to dict
        tool_call_dict = tool_call.model_dump(mode='json')
        
        assert tool_call_dict["tool_name"] == "create_task"
        assert tool_call_dict["success"] is True
        assert "2024-01-15T10:30:00+00:00" in tool_call_dict["timestamp"]
        assert tool_call_dict["parameters"] == {"title": "Test"}
    
    def test_tool_call_error_message_validation(self):
        """Test error message validation and cleaning."""
        # Test with whitespace-only error message
        tool_call = ToolCall(tool_name="create_task", error_message="   ")
        assert tool_call.error_message is None
        
        # Test with valid error message
        tool_call2 = ToolCall(tool_name="create_task", error_message="  Error occurred  ")
        assert tool_call2.error_message == "Error occurred"