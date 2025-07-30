"""
Unit tests for the MarkdownWriter class.

Tests Pydantic serialization, YAML generation, and markdown formatting.
"""

import pytest
from datetime import datetime, timezone

from src.todo_mcp.storage.markdown_writer import MarkdownWriter
from src.todo_mcp.models.task import Task
from src.todo_mcp.models.status import TaskStatus, Priority


class TestMarkdownWriter:
    """Test cases for MarkdownWriter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.writer = MarkdownWriter()
    
    def test_write_minimal_task_file(self):
        """Test writing a minimal task with only required fields."""
        task = Task(
            id="minimal-task",
            title="Minimal Task"
        )
        
        content = self.writer.write_task_file(task)
        
        assert "---" in content
        assert "id: minimal-task" in content
        assert "title: Minimal Task" in content
        assert "status: pending" in content
        assert "priority: 2" in content
        assert content.count("---") == 2
    
    def test_write_complete_task_file(self):
        """Test writing a complete task with all fields."""
        task = Task(
            id="complete-task",
            title="Complete Task",
            description="This is a complete task description.",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.HIGH,
            tags=["urgent", "backend"],
            parent_id="parent-task",
            child_ids=["child-1", "child-2"],
            due_date=datetime(2026, 1, 15, 18, 0, 0, tzinfo=timezone.utc),
            metadata={"project": "test-project", "estimate": 5}
        )
        
        content = self.writer.write_task_file(task)
        
        # Check frontmatter structure
        assert content.startswith("---\n")
        assert "---\n\n" in content
        
        # Check required fields
        assert "id: complete-task" in content
        assert "title: Complete Task" in content
        assert "status: in_progress" in content
        assert "priority: 3" in content
        
        # Check optional fields
        assert "tags:" in content
        assert "- urgent" in content
        assert "- backend" in content
        assert "parent_id: parent-task" in content
        assert "child_ids:" in content
        assert "- child-1" in content
        assert "- child-2" in content
        assert "due_date:" in content
        assert "metadata:" in content
        assert "project: test-project" in content
        
        # Check description
        assert "This is a complete task description." in content
    
    def test_prepare_frontmatter_pydantic_serialization(self):
        """Test frontmatter preparation using Pydantic serialization."""
        task = Task(
            id="test-task",
            title="Test Task",
            status=TaskStatus.COMPLETED,
            priority=Priority.LOW,
            tags=["test", "unit"],
            created_at=datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 2, 15, 30, 0, tzinfo=timezone.utc)
        )
        
        frontmatter = self.writer._prepare_frontmatter(task)
        
        assert frontmatter["id"] == "test-task"
        assert frontmatter["title"] == "Test Task"
        assert frontmatter["status"] == "completed"
        assert frontmatter["priority"] == 1
        assert frontmatter["tags"] == ["test", "unit"]
        assert "created_at" in frontmatter
        assert "updated_at" in frontmatter
    
    def test_format_task_content_empty(self):
        """Test formatting empty task content."""
        task = Task(id="empty", title="Empty", description="")
        
        content = self.writer.format_task_content(task)
        
        assert content == ""
    
    def test_format_task_content_with_text(self):
        """Test formatting task content with text."""
        task = Task(
            id="text-task",
            title="Text Task",
            description="Simple text content"
        )
        
        content = self.writer.format_task_content(task)
        
        assert content == "Simple text content\n"
    
    def test_serialize_task_data(self):
        """Test Pydantic serialization of task data."""
        task = Task(
            id="serialize-task",
            title="Serialize Task",
            status=TaskStatus.COMPLETED,
            priority=Priority.URGENT,
            tags=["serialization", "test"],
            metadata={"version": "1.0"}
        )
        
        data = self.writer.serialize_task_data(task)
        
        assert isinstance(data, dict)
        assert data["id"] == "serialize-task"
        assert data["title"] == "Serialize Task"
        assert data["status"] == "completed"
        assert data["priority"] == 4
        assert data["tags"] == ["serialization", "test"]
        assert data["metadata"]["version"] == "1.0"