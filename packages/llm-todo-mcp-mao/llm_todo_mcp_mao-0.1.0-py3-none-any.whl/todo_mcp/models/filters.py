"""
Task filtering models for the Todo MCP system.

This module defines Pydantic models for task filtering and querying
with type safety and validation.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from .status import TaskStatus, Priority


class TaskFilter(BaseModel):
    """
    Task filter model for advanced querying with Pydantic validation.
    
    This model defines all possible filter criteria for task queries
    with proper type validation and constraints.
    """
    
    # Status filtering
    status: Optional[List[TaskStatus]] = Field(
        default=None,
        description="Filter by task status(es)"
    )
    
    # Priority filtering
    priority: Optional[List[Priority]] = Field(
        default=None,
        description="Filter by task priority(ies)"
    )
    
    # Tag filtering
    tags: Optional[List[str]] = Field(
        default=None,
        description="Filter by tags (any match)"
    )
    
    tags_all: Optional[List[str]] = Field(
        default=None,
        description="Filter by tags (all must match)"
    )
    
    # Hierarchy filtering
    parent_id: Optional[str] = Field(
        default=None,
        description="Filter by parent task ID"
    )
    
    has_parent: Optional[bool] = Field(
        default=None,
        description="Filter by whether task has a parent"
    )
    
    has_children: Optional[bool] = Field(
        default=None,
        description="Filter by whether task has children"
    )
    
    # Date filtering
    created_after: Optional[datetime] = Field(
        default=None,
        description="Filter tasks created after this date"
    )
    
    created_before: Optional[datetime] = Field(
        default=None,
        description="Filter tasks created before this date"
    )
    
    updated_after: Optional[datetime] = Field(
        default=None,
        description="Filter tasks updated after this date"
    )
    
    updated_before: Optional[datetime] = Field(
        default=None,
        description="Filter tasks updated before this date"
    )
    
    due_after: Optional[datetime] = Field(
        default=None,
        description="Filter tasks due after this date"
    )
    
    due_before: Optional[datetime] = Field(
        default=None,
        description="Filter tasks due before this date"
    )
    
    has_due_date: Optional[bool] = Field(
        default=None,
        description="Filter by whether task has a due date"
    )
    
    # Text search
    search_text: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Full-text search in title and description"
    )
    
    title_contains: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Filter by title containing text"
    )
    
    description_contains: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Filter by description containing text"
    )
    
    # Result options
    include_completed: bool = Field(
        default=True,
        description="Include completed tasks in results"
    )
    
    limit: Optional[int] = Field(
        default=None,
        ge=1,
        le=1000,
        description="Maximum number of results to return"
    )
    
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of results to skip"
    )
    
    # Sorting
    sort_by: str = Field(
        default="created_at",
        description="Field to sort by"
    )
    
    sort_desc: bool = Field(
        default=True,
        description="Sort in descending order"
    )

    @field_validator('tags', 'tags_all')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate and clean tag lists."""
        if not v:
            return v
        
        # Clean and validate each tag
        cleaned_tags = []
        for tag in v:
            if isinstance(tag, str) and tag.strip():
                clean_tag = tag.strip().lower()
                if len(clean_tag) <= 50 and clean_tag not in cleaned_tags:
                    cleaned_tags.append(clean_tag)
        
        return cleaned_tags if cleaned_tags else None

    @field_validator('search_text', 'title_contains', 'description_contains')
    @classmethod
    def validate_search_text(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean search text."""
        if not v:
            return v
        
        cleaned = v.strip()
        return cleaned if cleaned else None

    @field_validator('sort_by')
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        """Validate sort field."""
        valid_fields = {
            'created_at', 'updated_at', 'due_date', 'title', 
            'status', 'priority', 'id'
        }
        
        if v not in valid_fields:
            raise ValueError(f"Invalid sort field: {v}. Valid fields: {', '.join(valid_fields)}")
        
        return v

    def has_filters(self) -> bool:
        """Check if any filters are applied."""
        filter_fields = [
            'status', 'priority', 'tags', 'tags_all', 'parent_id',
            'has_parent', 'has_children', 'created_after', 'created_before',
            'updated_after', 'updated_before', 'due_after', 'due_before',
            'has_due_date', 'search_text', 'title_contains', 'description_contains'
        ]
        
        return any(getattr(self, field) is not None for field in filter_fields)

    def is_empty(self) -> bool:
        """Check if filter is effectively empty (no filtering criteria)."""
        return not self.has_filters() and self.include_completed

    def __str__(self) -> str:
        """String representation of the filter."""
        active_filters = []
        
        if self.status:
            active_filters.append(f"status={[s.value for s in self.status]}")
        if self.priority:
            active_filters.append(f"priority={[p.name for p in self.priority]}")
        if self.tags:
            active_filters.append(f"tags={self.tags}")
        if self.search_text:
            active_filters.append(f"search='{self.search_text}'")
        if self.parent_id:
            active_filters.append(f"parent={self.parent_id}")
        
        if not active_filters:
            return "TaskFilter(no filters)"
        
        return f"TaskFilter({', '.join(active_filters)})"


class TaskSearchResult(BaseModel):
    """
    Task search result model with metadata.
    
    Contains the filtered tasks along with pagination and search metadata.
    """
    
    tasks: List = Field(
        description="List of tasks matching the filter"
    )
    
    total_count: int = Field(
        ge=0,
        description="Total number of tasks matching filter (before pagination)"
    )
    
    filtered_count: int = Field(
        ge=0,
        description="Number of tasks returned (after pagination)"
    )
    
    has_more: bool = Field(
        description="Whether there are more results available"
    )
    
    offset: int = Field(
        ge=0,
        description="Offset used for this result"
    )
    
    limit: Optional[int] = Field(
        default=None,
        ge=1,
        description="Limit used for this result"
    )
    
    filter_applied: TaskFilter = Field(
        description="Filter that was applied"
    )
    
    search_time_ms: Optional[float] = Field(
        default=None,
        ge=0,
        description="Time taken to execute search in milliseconds"
    )

    def __str__(self) -> str:
        """String representation of search result."""
        return f"TaskSearchResult({self.filtered_count}/{self.total_count} tasks)"