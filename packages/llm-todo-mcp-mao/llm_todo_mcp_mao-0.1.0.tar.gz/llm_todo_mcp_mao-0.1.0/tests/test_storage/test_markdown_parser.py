"""
Unit tests for the MarkdownParser class.

Tests YAML frontmatter parsing, Pydantic validation, and error handling.
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from src.todo_mcp.storage.markdown_parser import MarkdownParser, MarkdownParseError
from src.todo_mcp.models.task import Task
from src.todo_mcp.models.status import TaskStatus, Priority


class TestMarkdownParser:
    """Test cases for MarkdownParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = MarkdownParser()
    
    def test_parse_valid_task_file(self):
        """Test parsing a valid task file with YAML frontmatter."""
        content = """---
id: task-001
title: Test Task
status: pending
priority: high
tags:
  - urgent
  - backend
parent_id: null
child_ids: []
created_at: 2025-01-01T10:00:00Z
updated_at: 2025-01-01T10:00:00Z
due_date: 2026-01-15T18:00:00Z
tool_calls: []
metadata: {}
---

This is a test task description with **markdown** formatting.

- Item 1
- Item 2
"""
        
        task = self.parser.parse_task_file(content)
        
        assert task.id == "task-001"
        assert task.title == "Test Task"
        assert task.status == TaskStatus.PENDING.value
        assert task.priority == Priority.HIGH.value
        assert "urgent" in task.tags
        assert "backend" in task.tags
        assert "This is a test task description" in task.description
        assert task.due_date is not None
    
    def test_parse_minimal_task_file(self):
        """Test parsing a minimal task file with only required fields."""
        content = """---
id: minimal-task
title: Minimal Task
---

Simple description.
"""
        
        task = self.parser.parse_task_file(content)
        
        assert task.id == "minimal-task"
        assert task.title == "Minimal Task"
        assert task.status == TaskStatus.PENDING  # Default value
        assert task.priority == Priority.MEDIUM  # Default value
        assert task.description == "Simple description."
        assert task.tags == []
        assert task.child_ids == []
    
    def test_parse_task_with_string_enums(self):
        """Test parsing task with string enum values."""
        content = """---
id: enum-test
title: Enum Test
status: in_progress
priority: urgent
---

Testing enum conversion.
"""
        
        task = self.parser.parse_task_file(content)
        
        assert task.status == TaskStatus.IN_PROGRESS.value
        assert task.priority == Priority.URGENT.value
    
    def test_parse_task_with_comma_separated_tags(self):
        """Test parsing task with comma-separated tags string."""
        content = """---
id: tags-test
title: Tags Test
tags: frontend, javascript, react
---

Testing tag parsing.
"""
        
        task = self.parser.parse_task_file(content)
        
        assert "frontend" in task.tags
        assert "javascript" in task.tags
        assert "react" in task.tags
        assert len(task.tags) == 3
    
    def test_parse_task_with_comma_separated_child_ids(self):
        """Test parsing task with comma-separated child IDs."""
        content = """---
id: parent-task
title: Parent Task
child_ids: child-1, child-2, child-3
---

Parent task with children.
"""
        
        task = self.parser.parse_task_file(content)
        
        assert "child-1" in task.child_ids
        assert "child-2" in task.child_ids
        assert "child-3" in task.child_ids
        assert len(task.child_ids) == 3
    
    def test_parse_task_no_frontmatter(self):
        """Test parsing task file without YAML frontmatter."""
        content = "Just a plain markdown file without frontmatter."
        
        with pytest.raises(MarkdownParseError, match="No YAML frontmatter found"):
            self.parser.parse_task_file(content)
    
    def test_parse_task_invalid_yaml(self):
        """Test parsing task with invalid YAML frontmatter."""
        content = """---
id: invalid-yaml
title: [unclosed bracket
status: pending
---

Invalid YAML content.
"""
        
        with pytest.raises(MarkdownParseError, match="Invalid YAML frontmatter"):
            self.parser.parse_task_file(content)
    
    def test_parse_task_missing_required_fields(self):
        """Test parsing task missing required fields."""
        content = """---
title: Missing ID Task
status: pending
---

Task without ID.
"""
        
        with pytest.raises(ValidationError):
            self.parser.parse_task_file(content)
    
    def test_parse_task_invalid_status(self):
        """Test parsing task with invalid status value."""
        content = """---
id: invalid-status
title: Invalid Status Task
status: invalid_status
---

Task with invalid status.
"""
        
        task = self.parser.parse_task_file(content)
        # Should default to PENDING with warning
        assert task.status == TaskStatus.PENDING.value
    
    def test_parse_task_invalid_priority(self):
        """Test parsing task with invalid priority value."""
        content = """---
id: invalid-priority
title: Invalid Priority Task
priority: super_urgent
---

Task with invalid priority.
"""
        
        task = self.parser.parse_task_file(content)
        # Should default to MEDIUM with warning
        assert task.priority == Priority.MEDIUM
    
    def test_parse_task_invalid_datetime(self):
        """Test parsing task with invalid datetime format."""
        content = """---
id: invalid-date
title: Invalid Date Task
created_at: "not-a-date"
due_date: "invalid-date-format"
---

Task with invalid dates.
"""
        
        task = self.parser.parse_task_file(content)
        # Should handle invalid dates gracefully
        assert isinstance(task.created_at, datetime)
        assert task.due_date is None
    
    def test_extract_frontmatter_valid(self):
        """Test extracting valid YAML frontmatter."""
        content = """---
key: value
---
Body content here."""
        
        frontmatter, body = self.parser._extract_frontmatter(content)
        
        assert frontmatter == "key: value"
        assert body == "Body content here."
    
    def test_extract_frontmatter_no_frontmatter(self):
        """Test extracting from content without frontmatter."""
        content = "Just body content without frontmatter."
        
        frontmatter, body = self.parser._extract_frontmatter(content)
        
        assert frontmatter is None
        assert body == "Just body content without frontmatter."
    
    def test_extract_frontmatter_empty_content(self):
        """Test extracting from empty content."""
        content = ""
        
        frontmatter, body = self.parser._extract_frontmatter(content)
        
        assert frontmatter is None
        assert body == ""
    
    def test_convert_field_types_status(self):
        """Test status field type conversion."""
        data = {"status": "completed"}
        
        converted = self.parser._convert_field_types(data)
        
        assert converted["status"] == "completed"
    
    def test_convert_field_types_priority(self):
        """Test priority field type conversion."""
        data = {"priority": "low"}
        
        converted = self.parser._convert_field_types(data)
        
        assert converted["priority"] == Priority.LOW.value
    
    def test_convert_field_types_datetime(self):
        """Test datetime field type conversion."""
        data = {
            "created_at": "2025-01-01T10:00:00Z",
            "updated_at": "2025-01-01T11:00:00+00:00",
            "due_date": "2025-01-15T18:00:00Z"
        }
        
        converted = self.parser._convert_field_types(data)
        
        assert isinstance(converted["created_at"], datetime)
        assert isinstance(converted["updated_at"], datetime)
        assert isinstance(converted["due_date"], datetime)
    
    def test_convert_field_types_tags_string(self):
        """Test tags field conversion from string."""
        data = {"tags": "tag1, tag2, tag3"}
        
        converted = self.parser._convert_field_types(data)
        
        assert converted["tags"] == ["tag1", "tag2", "tag3"]
    
    def test_convert_field_types_child_ids_string(self):
        """Test child_ids field conversion from string."""
        data = {"child_ids": "child1, child2, child3"}
        
        converted = self.parser._convert_field_types(data)
        
        assert converted["child_ids"] == ["child1", "child2", "child3"]
    
    def test_validate_task_structure_valid(self):
        """Test validation of valid task structure."""
        metadata = {
            "id": "valid-task",
            "title": "Valid Task"
        }
        
        result = self.parser.validate_task_structure(metadata)
        
        assert result is True
    
    def test_validate_task_structure_missing_id(self):
        """Test validation with missing ID."""
        metadata = {
            "title": "Task without ID"
        }
        
        result = self.parser.validate_task_structure(metadata)
        
        assert result is False
    
    def test_validate_task_structure_missing_title(self):
        """Test validation with missing title."""
        metadata = {
            "id": "task-without-title"
        }
        
        result = self.parser.validate_task_structure(metadata)
        
        assert result is False
    
    def test_validate_task_structure_empty_fields(self):
        """Test validation with empty required fields."""
        metadata = {
            "id": "",
            "title": "   "
        }
        
        result = self.parser.validate_task_structure(metadata)
        
        assert result is False
    
    def test_parse_multiple_tasks_single_task(self):
        """Test parsing multiple tasks with single task content."""
        content = """---
id: single-task
title: Single Task
---

Single task content.
"""
        
        tasks = self.parser.parse_multiple_tasks(content)
        
        assert len(tasks) == 1
        assert tasks[0].id == "single-task"
    
    def test_parse_multiple_tasks_empty_content(self):
        """Test parsing multiple tasks with empty content."""
        content = ""
        
        tasks = self.parser.parse_multiple_tasks(content)
        
        assert len(tasks) == 0
    
    def test_pydantic_validation_error_handling(self):
        """Test proper handling of Pydantic validation errors."""
        content = """---
id: ""
title: ""
status: pending
---

Task with empty required fields.
"""
        
        with pytest.raises(ValidationError):
            self.parser.parse_task_file(content)
    
    def test_complex_task_with_all_fields(self):
        """Test parsing a complex task with all possible fields."""
        content = """---
id: complex-task-001
title: Complex Task with All Fields
description: Initial description
status: in_progress
priority: urgent
tags:
  - critical
  - backend
  - database
parent_id: parent-task-001
child_ids:
  - child-task-001
  - child-task-002
created_at: 2025-01-01T08:00:00Z
updated_at: 2025-01-02T14:30:00Z
due_date: 2026-01-31T23:59:59Z
tool_calls:
  - tool_name: create_task
    timestamp: 2025-01-01T08:00:00Z
    success: true
metadata:
  project: web-app
  sprint: sprint-1
  estimate: 8
---

# Complex Task Description

This is a **complex task** with:

1. Multiple tags
2. Parent-child relationships
3. Tool call history
4. Custom metadata

## Requirements

- Implement feature X
- Write unit tests
- Update documentation

## Notes

This task requires careful attention to detail.
"""
        
        task = self.parser.parse_task_file(content)
        
        # Verify all fields are parsed correctly
        assert task.id == "complex-task-001"
        assert task.title == "Complex Task with All Fields"
        assert task.status == TaskStatus.IN_PROGRESS.value
        assert task.priority == Priority.URGENT.value
        assert len(task.tags) == 3
        assert "critical" in task.tags
        assert task.parent_id == "parent-task-001"
        assert len(task.child_ids) == 2
        assert "child-task-001" in task.child_ids
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
        assert isinstance(task.due_date, datetime)
        assert len(task.tool_calls) == 1
        assert "project" in task.metadata
        assert task.metadata["project"] == "web-app"
        assert "# Complex Task Description" in task.description