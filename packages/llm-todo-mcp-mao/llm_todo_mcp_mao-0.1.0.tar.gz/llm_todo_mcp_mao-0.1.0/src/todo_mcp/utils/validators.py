"""
Input validation utilities for the Todo MCP system.

This module provides validation functions for task data,
ensuring data integrity and proper formatting.
"""

import re
from typing import Any, List, Optional

from ..models.task import Priority, TaskStatus


def validate_task_id(task_id: str) -> bool:
    """
    Validate task ID format.
    
    Args:
        task_id: Task identifier to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not task_id or not isinstance(task_id, str):
        return False
    
    # Task ID should be alphanumeric with optional hyphens/underscores
    pattern = r'^[a-zA-Z0-9_-]+$'
    
    return bool(re.match(pattern, task_id)) and len(task_id) <= 50


def validate_task_title(title: str) -> bool:
    """
    Validate task title.
    
    Args:
        title: Task title to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not title or not isinstance(title, str):
        return False
    
    # Title should not be empty and within reasonable length
    title = title.strip()
    return 1 <= len(title) <= 200


def validate_priority(priority: Any) -> bool:
    """
    Validate task priority.
    
    Args:
        priority: Priority value to validate
        
    Returns:
        True if valid, False otherwise
    """
    if isinstance(priority, Priority):
        return True
    
    if isinstance(priority, str):
        try:
            Priority(priority.lower())
            return True
        except ValueError:
            return False
    
    return False


def validate_status(status: Any) -> bool:
    """
    Validate task status.
    
    Args:
        status: Status value to validate
        
    Returns:
        True if valid, False otherwise
    """
    if isinstance(status, TaskStatus):
        return True
    
    if isinstance(status, str):
        try:
            TaskStatus(status.lower())
            return True
        except ValueError:
            return False
    
    return False


def validate_tags(tags: List[str]) -> bool:
    """
    Validate task tags.
    
    Args:
        tags: List of tags to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(tags, list):
        return False
    
    for tag in tags:
        if not isinstance(tag, str) or not tag.strip():
            return False
        
        # Tag should be reasonable length and contain valid characters
        if len(tag.strip()) > 50:
            return False
        
        # Tags should not contain special characters that could cause issues
        if re.search(r'[<>"\']', tag):
            return False
    
    return True


def validate_description(description: str) -> bool:
    """
    Validate task description.
    
    Args:
        description: Description to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(description, str):
        return False
    
    # Description can be empty but should not exceed reasonable length
    return len(description) <= 10000


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing potentially harmful content.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove null bytes and control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def validate_parent_child_relationship(parent_id: str, child_id: str) -> bool:
    """
    Validate parent-child relationship.
    
    Args:
        parent_id: Parent task ID
        child_id: Child task ID
        
    Returns:
        True if valid, False otherwise
    """
    # Basic validation
    if not validate_task_id(parent_id) or not validate_task_id(child_id):
        return False
    
    # Parent and child cannot be the same
    if parent_id == child_id:
        return False
    
    return True


def validate_task_data(data: dict) -> List[str]:
    """
    Validate complete task data and return list of errors.
    
    Args:
        data: Task data dictionary
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Required fields
    if 'id' not in data or not validate_task_id(data['id']):
        errors.append("Invalid or missing task ID")
    
    if 'title' not in data or not validate_task_title(data['title']):
        errors.append("Invalid or missing task title")
    
    # Optional fields
    if 'priority' in data and not validate_priority(data['priority']):
        errors.append("Invalid priority value")
    
    if 'status' in data and not validate_status(data['status']):
        errors.append("Invalid status value")
    
    if 'tags' in data and not validate_tags(data['tags']):
        errors.append("Invalid tags format")
    
    if 'description' in data and not validate_description(data['description']):
        errors.append("Invalid description")
    
    return errors