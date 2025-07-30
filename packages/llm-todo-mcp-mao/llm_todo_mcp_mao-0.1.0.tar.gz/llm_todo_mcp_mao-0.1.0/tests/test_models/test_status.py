"""
Unit tests for the status models and functionality.

This module tests the TaskStatus and Priority enums,
status transitions, and related functionality.
"""

import pytest

from src.todo_mcp.models.status import (
    TaskStatus,
    Priority,
    StatusTransitionError,
    is_valid_status_transition,
    validate_status_transition,
    get_valid_transitions,
    get_status_description,
    get_priority_description,
)


class TestTaskStatus:
    """Test cases for the TaskStatus enum."""
    
    def test_status_values(self):
        """Test that status enum has correct values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.BLOCKED.value == "blocked"
    
    def test_status_string_representation(self):
        """Test status string representation."""
        assert str(TaskStatus.PENDING) == "pending"
        assert str(TaskStatus.IN_PROGRESS) == "in_progress"
    
    def test_status_from_string(self):
        """Test creating status from string."""
        assert TaskStatus.from_string("pending") == TaskStatus.PENDING
        assert TaskStatus.from_string("COMPLETED") == TaskStatus.COMPLETED
        
        with pytest.raises(ValueError):
            TaskStatus.from_string("invalid")


class TestPriority:
    """Test cases for the Priority enum."""
    
    def test_priority_values(self):
        """Test that priority enum has correct values."""
        assert Priority.LOW.value == 1
        assert Priority.MEDIUM.value == 2
        assert Priority.HIGH.value == 3
        assert Priority.URGENT.value == 4
    
    def test_priority_comparison(self):
        """Test priority comparison operations."""
        assert Priority.URGENT > Priority.HIGH
        assert Priority.HIGH > Priority.MEDIUM
        assert Priority.MEDIUM > Priority.LOW
        
        assert Priority.LOW < Priority.URGENT
        assert Priority.MEDIUM <= Priority.HIGH
        assert Priority.HIGH >= Priority.MEDIUM
    
    def test_priority_string_representation(self):
        """Test priority string representation."""
        assert str(Priority.LOW) == "low"
        assert str(Priority.URGENT) == "urgent"
    
    def test_priority_from_string(self):
        """Test creating priority from string."""
        assert Priority.from_string("low") == Priority.LOW
        assert Priority.from_string("HIGH") == Priority.HIGH
        
        with pytest.raises(ValueError):
            Priority.from_string("invalid")
    
    def test_priority_comparison_methods(self):
        """Test priority comparison helper methods."""
        assert Priority.HIGH.is_higher_than(Priority.MEDIUM)
        assert Priority.LOW.is_lower_than(Priority.HIGH)
        assert not Priority.MEDIUM.is_higher_than(Priority.HIGH)
        assert not Priority.HIGH.is_lower_than(Priority.MEDIUM)


class TestStatusTransitions:
    """Test cases for status transition functionality."""
    
    def test_valid_transitions(self):
        """Test valid status transitions."""
        # From PENDING
        assert is_valid_status_transition(TaskStatus.PENDING, TaskStatus.IN_PROGRESS)
        assert is_valid_status_transition(TaskStatus.PENDING, TaskStatus.BLOCKED)
        assert is_valid_status_transition(TaskStatus.PENDING, TaskStatus.COMPLETED)
        
        # From IN_PROGRESS
        assert is_valid_status_transition(TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED)
        assert is_valid_status_transition(TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED)
        assert is_valid_status_transition(TaskStatus.IN_PROGRESS, TaskStatus.PENDING)
        
        # From COMPLETED (allow reopening)
        assert is_valid_status_transition(TaskStatus.COMPLETED, TaskStatus.PENDING)
        assert is_valid_status_transition(TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS)
        
        # From BLOCKED
        assert is_valid_status_transition(TaskStatus.BLOCKED, TaskStatus.PENDING)
        assert is_valid_status_transition(TaskStatus.BLOCKED, TaskStatus.IN_PROGRESS)
    
    def test_invalid_transitions(self):
        """Test invalid status transitions."""
        # COMPLETED cannot go directly to BLOCKED
        assert not is_valid_status_transition(TaskStatus.COMPLETED, TaskStatus.BLOCKED)
        
        # BLOCKED cannot go directly to COMPLETED
        assert not is_valid_status_transition(TaskStatus.BLOCKED, TaskStatus.COMPLETED)
    
    def test_get_valid_transitions(self):
        """Test getting valid transitions for a status."""
        pending_transitions = get_valid_transitions(TaskStatus.PENDING)
        assert TaskStatus.IN_PROGRESS in pending_transitions
        assert TaskStatus.BLOCKED in pending_transitions
        assert TaskStatus.COMPLETED in pending_transitions
        
        completed_transitions = get_valid_transitions(TaskStatus.COMPLETED)
        assert TaskStatus.PENDING in completed_transitions
        assert TaskStatus.IN_PROGRESS in completed_transitions
        assert TaskStatus.BLOCKED not in completed_transitions
    
    def test_validate_status_transition_success(self):
        """Test successful status transition validation."""
        # Should not raise exception for valid transitions
        validate_status_transition(TaskStatus.PENDING, TaskStatus.IN_PROGRESS)
        validate_status_transition(TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED)
    
    def test_validate_status_transition_failure(self):
        """Test status transition validation failure."""
        with pytest.raises(StatusTransitionError) as exc_info:
            validate_status_transition(TaskStatus.COMPLETED, TaskStatus.BLOCKED)
        
        error = exc_info.value
        assert error.from_status == TaskStatus.COMPLETED
        assert error.to_status == TaskStatus.BLOCKED
        assert "Invalid status transition" in str(error)


class TestStatusDescriptions:
    """Test cases for status and priority descriptions."""
    
    def test_status_descriptions(self):
        """Test status description functionality."""
        assert "waiting to be started" in get_status_description(TaskStatus.PENDING)
        assert "currently being worked on" in get_status_description(TaskStatus.IN_PROGRESS)
        assert "finished successfully" in get_status_description(TaskStatus.COMPLETED)
        assert "blocked" in get_status_description(TaskStatus.BLOCKED)
    
    def test_priority_descriptions(self):
        """Test priority description functionality."""
        assert "Low priority" in get_priority_description(Priority.LOW)
        assert "Medium priority" in get_priority_description(Priority.MEDIUM)
        assert "High priority" in get_priority_description(Priority.HIGH)
        assert "Urgent priority" in get_priority_description(Priority.URGENT)