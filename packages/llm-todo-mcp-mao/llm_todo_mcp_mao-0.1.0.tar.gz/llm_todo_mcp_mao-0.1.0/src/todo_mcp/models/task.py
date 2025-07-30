"""
Task model and related enums for the Todo MCP system.

This module defines the core Task data model using Pydantic for validation
and serialization, along with TaskStatus and Priority enums.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from .status import TaskStatus, Priority


class Task(BaseModel):
    """
    Core Task model with hierarchy support and validation.
    
    This model represents a task with all its properties, relationships,
    and metadata. Uses Pydantic for automatic validation and serialization.
    """
    
    id: str = Field(..., description="Unique task identifier")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str = Field(default="", description="Detailed task description")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status")
    priority: Priority = Field(default=Priority.MEDIUM, description="Task priority level")
    tags: List[str] = Field(default_factory=list, description="Task tags for categorization")
    parent_id: Optional[str] = Field(default=None, description="Parent task ID for hierarchy")
    child_ids: List[str] = Field(default_factory=list, description="Child task IDs")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    due_date: Optional[datetime] = Field(default=None, description="Task due date")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="Tool call history")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata")

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
        },
    }

    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate task ID is not empty and follows proper format."""
        if not v or not v.strip():
            raise ValueError('Task ID cannot be empty')
        
        # Ensure ID contains only valid characters
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v.strip()):
            raise ValueError('Task ID can only contain letters, numbers, underscores, and hyphens')
        
        return v.strip()

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate task title length and content."""
        if not v or not v.strip():
            raise ValueError('Task title cannot be empty')
        
        title = v.strip()
        if len(title) > 200:
            raise ValueError('Task title cannot exceed 200 characters')
        
        return title

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate and clean task tags."""
        if not v:
            return []
        
        # Clean and validate each tag
        cleaned_tags = []
        for tag in v:
            if isinstance(tag, str) and tag.strip():
                clean_tag = tag.strip().lower()
                if len(clean_tag) <= 50 and clean_tag not in cleaned_tags:
                    cleaned_tags.append(clean_tag)
        
        return cleaned_tags

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate due date is not in the past."""
        if v is None:
            return v
        
        # Allow some flexibility for dates set in the recent past (within 1 hour)
        from datetime import timedelta, timezone
        
        # Ensure we're comparing timezone-aware datetimes
        now = datetime.now(timezone.utc)
        min_allowed = now - timedelta(hours=1)
        
        # Convert to UTC if timezone-aware, otherwise assume UTC
        due_date = v
        if v.tzinfo is None:
            due_date = v.replace(tzinfo=timezone.utc)
        
        if due_date < min_allowed:
            raise ValueError('Due date cannot be significantly in the past')
        
        return v

    @model_validator(mode='after')
    def validate_hierarchy(self) -> 'Task':
        """Validate task hierarchy relationships."""
        # Prevent self-referencing
        if self.parent_id == self.id:
            raise ValueError('Task cannot be its own parent')
        
        # Prevent self in children
        if self.id in self.child_ids:
            raise ValueError('Task cannot be its own child')
        
        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.utcnow()

    def add_child(self, child_id: str) -> None:
        """Add a child task ID if not already present."""
        if child_id != self.id and child_id not in self.child_ids:
            self.child_ids.append(child_id)
            self.update_timestamp()

    def remove_child(self, child_id: str) -> None:
        """Remove a child task ID if present."""
        if child_id in self.child_ids:
            self.child_ids.remove(child_id)
            self.update_timestamp()

    def __str__(self) -> str:
        """String representation of the task."""
        return f"Task({self.id}: {self.title})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Task(id='{self.id}', title='{self.title}', status='{self.status.value}')"