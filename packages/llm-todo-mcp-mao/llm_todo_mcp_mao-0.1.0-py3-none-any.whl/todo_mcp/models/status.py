"""
Task status definitions and related functionality.

This module contains the TaskStatus enum and related status management
functionality for the Todo MCP system.
"""

from enum import Enum, IntEnum
from typing import Dict, List, Set, Optional


class TaskStatus(Enum):
    """
    Task status enumeration with transition rules.
    
    Defines all possible task states and valid transitions between them.
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    BLOCKED = "blocked"

    def __str__(self) -> str:
        """String representation of the status."""
        return self.value

    @classmethod
    def from_string(cls, status_str: str) -> 'TaskStatus':
        """Create TaskStatus from string value."""
        try:
            return cls(status_str.lower())
        except ValueError:
            raise ValueError(f"Invalid task status: {status_str}")


class Priority(IntEnum):
    """
    Task priority enumeration with comparison support.
    
    Uses IntEnum to enable priority comparison operations.
    Higher numeric values indicate higher priority.
    """
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

    def __str__(self) -> str:
        """String representation of the priority."""
        return self.name.lower()

    @classmethod
    def from_string(cls, priority_str: str) -> 'Priority':
        """Create Priority from string value."""
        try:
            return cls[priority_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid priority: {priority_str}")

    def is_higher_than(self, other: 'Priority') -> bool:
        """Check if this priority is higher than another."""
        return self.value > other.value

    def is_lower_than(self, other: 'Priority') -> bool:
        """Check if this priority is lower than another."""
        return self.value < other.value


# Valid status transitions mapping
STATUS_TRANSITIONS: Dict[TaskStatus, Set[TaskStatus]] = {
    TaskStatus.PENDING: {TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.COMPLETED},
    TaskStatus.IN_PROGRESS: {TaskStatus.COMPLETED, TaskStatus.BLOCKED, TaskStatus.PENDING},
    TaskStatus.COMPLETED: {TaskStatus.PENDING, TaskStatus.IN_PROGRESS},  # Allow reopening
    TaskStatus.BLOCKED: {TaskStatus.PENDING, TaskStatus.IN_PROGRESS},
}


class StatusTransitionError(ValueError):
    """Exception raised when an invalid status transition is attempted."""
    
    def __init__(self, from_status: TaskStatus, to_status: TaskStatus):
        self.from_status = from_status
        self.to_status = to_status
        valid_transitions = get_valid_transitions(from_status)
        valid_str = ", ".join([s.value for s in valid_transitions])
        super().__init__(
            f"Invalid status transition from '{from_status.value}' to '{to_status.value}'. "
            f"Valid transitions from '{from_status.value}' are: {valid_str}"
        )


def is_valid_status_transition(from_status: TaskStatus, to_status: TaskStatus) -> bool:
    """
    Check if a status transition is valid.
    
    Args:
        from_status: Current task status
        to_status: Desired new status
        
    Returns:
        True if transition is valid, False otherwise
    """
    return to_status in STATUS_TRANSITIONS.get(from_status, set())


def validate_status_transition(from_status: TaskStatus, to_status: TaskStatus) -> None:
    """
    Validate a status transition and raise an exception if invalid.
    
    Args:
        from_status: Current task status
        to_status: Desired new status
        
    Raises:
        StatusTransitionError: If the transition is not valid
    """
    if not is_valid_status_transition(from_status, to_status):
        raise StatusTransitionError(from_status, to_status)


def get_valid_transitions(status: TaskStatus) -> List[TaskStatus]:
    """
    Get all valid status transitions from the current status.
    
    Args:
        status: Current task status
        
    Returns:
        List of valid target statuses
    """
    return list(STATUS_TRANSITIONS.get(status, set()))


def get_status_description(status: TaskStatus) -> str:
    """
    Get a human-readable description of the task status.
    
    Args:
        status: Task status
        
    Returns:
        Description string
    """
    descriptions = {
        TaskStatus.PENDING: "Task is waiting to be started",
        TaskStatus.IN_PROGRESS: "Task is currently being worked on",
        TaskStatus.COMPLETED: "Task has been finished successfully",
        TaskStatus.BLOCKED: "Task is blocked and cannot proceed",
    }
    return descriptions.get(status, "Unknown status")


def get_priority_description(priority: Priority) -> str:
    """
    Get a human-readable description of the task priority.
    
    Args:
        priority: Task priority
        
    Returns:
        Description string
    """
    descriptions = {
        Priority.LOW: "Low priority - can be done when time permits",
        Priority.MEDIUM: "Medium priority - normal importance",
        Priority.HIGH: "High priority - should be done soon",
        Priority.URGENT: "Urgent priority - needs immediate attention",
    }
    return descriptions.get(priority, "Unknown priority")