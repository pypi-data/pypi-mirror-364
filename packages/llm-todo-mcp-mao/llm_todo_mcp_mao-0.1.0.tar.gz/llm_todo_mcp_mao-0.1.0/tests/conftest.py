"""
Pytest configuration and shared fixtures for the Todo MCP system.

This module provides common test fixtures and configuration
for all test modules in the project.
"""

import pytest
import tempfile
from pathlib import Path
from typing import Generator

from src.todo_mcp.config import TodoConfig
from src.todo_mcp.models.task import Task, TaskStatus, Priority


@pytest.fixture
def temp_data_dir() -> Generator[Path, None, None]:
    """
    Create a temporary directory for test data.
    
    Yields:
        Path to temporary directory
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def test_config(temp_data_dir: Path) -> TodoConfig:
    """
    Create a test configuration with temporary data directory.
    
    Args:
        temp_data_dir: Temporary directory fixture
        
    Returns:
        Test configuration
    """
    config = TodoConfig(
        data_directory=temp_data_dir,
        backup_enabled=False,
        file_watch_enabled=False,
        log_level="DEBUG",
    )
    
    # Ensure directories exist
    config.data_directory.mkdir(parents=True, exist_ok=True)
    (config.data_directory / "tasks").mkdir(exist_ok=True)
    (config.data_directory / "templates").mkdir(exist_ok=True)
    
    return config


@pytest.fixture
def sample_task() -> Task:
    """
    Create a sample task for testing.
    
    Returns:
        Sample Task object
    """
    return Task(
        id="test-001",
        title="Test Task",
        description="This is a test task for unit testing",
        status=TaskStatus.PENDING,
        priority=Priority.MEDIUM,
        tags=["test", "sample"],
    )


@pytest.fixture
def sample_task_data() -> dict:
    """
    Create sample task data dictionary.
    
    Returns:
        Sample task data
    """
    return {
        "id": "test-002",
        "title": "Another Test Task",
        "description": "Another test task with different data",
        "status": "in_progress",
        "priority": "high",
        "tags": ["test", "important"],
    }


@pytest.fixture
def sample_markdown_content() -> str:
    """
    Create sample markdown content for testing.
    
    Returns:
        Sample markdown content with frontmatter
    """
    return """---
id: test-003
title: Markdown Test Task
status: pending
priority: medium
tags:
  - test
  - markdown
created_at: 2024-01-01T00:00:00Z
updated_at: 2024-01-01T00:00:00Z
---

This is a test task created from markdown content.

## Details

- This task is for testing markdown parsing
- It includes YAML frontmatter
- The content is in markdown format
"""