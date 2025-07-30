"""
Unit tests for the Task model.

This module tests the Task model validation, serialization,
and basic functionality.
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from src.todo_mcp.models.task import Task, TaskStatus, Priority


class TestTask:
    """Test cases for the Task model."""
    
    def test_task_creation_minimal(self):
        """Test creating a task with minimal required fields."""
        task = Task(id="test-001", title="Test Task")
        
        assert task.id == "test-001"
        assert task.title == "Test Task"
        assert task.description == ""
        assert task.status == TaskStatus.PENDING
        assert task.priority == Priority.MEDIUM
        assert task.tags == []
        assert task.parent_id is None
        assert task.child_ids == []
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
        assert task.due_date is None
        assert task.tool_calls == []
        assert task.metadata == {}
    
    def test_task_creation_full(self):
        """Test creating a task with all fields."""
        due_date = datetime.now(timezone.utc)
        
        task = Task(
            id="test-002",
            title="Full Test Task",
            description="A complete test task",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.HIGH,
            tags=["test", "important"],
            parent_id="parent-001",
            child_ids=["child-001", "child-002"],
            due_date=due_date,
            metadata={"custom": "value"}
        )
        
        assert task.id == "test-002"
        assert task.title == "Full Test Task"
        assert task.description == "A complete test task"
        assert task.status == TaskStatus.IN_PROGRESS.value
        assert task.priority == Priority.HIGH.value
        assert task.tags == ["test", "important"]
        assert task.parent_id == "parent-001"
        assert task.child_ids == ["child-001", "child-002"]
        assert task.due_date == due_date
        assert task.metadata == {"custom": "value"}
    
    def test_task_validation_empty_id(self):
        """Test that empty ID raises validation error."""
        with pytest.raises(ValidationError):
            Task(id="", title="Test Task")
    
    def test_task_validation_invalid_id_characters(self):
        """Test that invalid ID characters raise validation error."""
        with pytest.raises(ValidationError):
            Task(id="test@001", title="Test Task")
        
        with pytest.raises(ValidationError):
            Task(id="test 001", title="Test Task")
    
    def test_task_validation_empty_title(self):
        """Test that empty title raises validation error."""
        with pytest.raises(ValidationError):
            Task(id="test-001", title="")
    
    def test_task_validation_long_title(self):
        """Test that overly long title raises validation error."""
        long_title = "x" * 201  # Exceeds 200 character limit
        
        with pytest.raises(ValidationError):
            Task(id="test-001", title=long_title)
    
    def test_task_validation_tags_cleaning(self):
        """Test that tags are properly cleaned and validated."""
        task = Task(
            id="test-001",
            title="Test Task",
            tags=["  Important  ", "URGENT", "important", "", "work"]
        )
        
        # Should clean whitespace, convert to lowercase, and remove duplicates
        assert "important" in task.tags
        assert "urgent" in task.tags
        assert "work" in task.tags
        assert len(task.tags) == 3  # No duplicates or empty tags
    
    def test_task_validation_self_parent(self):
        """Test that task cannot be its own parent."""
        with pytest.raises(ValidationError):
            Task(id="test-001", title="Test Task", parent_id="test-001")
    
    def test_task_validation_self_child(self):
        """Test that task cannot be its own child."""
        with pytest.raises(ValidationError):
            Task(id="test-001", title="Test Task", child_ids=["test-001"])
    
    def test_task_hierarchy_methods(self):
        """Test task hierarchy management methods."""
        task = Task(id="test-001", title="Test Task")
        
        # Test adding child
        task.add_child("child-001")
        assert "child-001" in task.child_ids
        
        # Test adding duplicate child (should not duplicate)
        task.add_child("child-001")
        assert task.child_ids.count("child-001") == 1
        
        # Test removing child
        task.remove_child("child-001")
        assert "child-001" not in task.child_ids
        
        # Test removing non-existent child (should not error)
        task.remove_child("non-existent")
    
    def test_task_update_timestamp(self):
        """Test that update_timestamp method works."""
        task = Task(id="test-001", title="Test Task")
        original_time = task.updated_at
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        task.update_timestamp()
        assert task.updated_at > original_time
    
    def test_task_string_representation(self):
        """Test task string representations."""
        task = Task(id="test-001", title="Test Task")
        
        assert str(task) == "Task(test-001: Test Task)"
        assert "test-001" in repr(task)
        assert "Test Task" in repr(task)
        assert "pending" in repr(task)
    
    def test_task_serialization(self):
        """Test task JSON serialization."""
        task = Task(id="test-001", title="Test Task")
        
        # Test that task can be serialized to dict
        task_dict = task.model_dump(mode='json')
        
        assert task_dict["id"] == "test-001"
        assert task_dict["title"] == "Test Task"
        assert task_dict["status"] == "pending"
        assert task_dict["priority"] == 2  # Priority.MEDIUM.value
    
    def test_task_enum_values(self):
        """Test that enum values are properly handled."""
        task = Task(
            id="test-001",
            title="Test Task",
            status=TaskStatus.COMPLETED,  # Enum value
            priority=Priority.URGENT      # Enum value
        )
        
        assert task.status == TaskStatus.COMPLETED.value
        assert task.priority == Priority.URGENT.value