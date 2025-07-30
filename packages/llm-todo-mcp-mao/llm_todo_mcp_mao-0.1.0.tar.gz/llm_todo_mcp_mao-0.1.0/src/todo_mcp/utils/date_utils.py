"""
Date and time utilities for the Todo MCP system.

This module provides utility functions for date/time parsing,
formatting, and validation operations.
"""

from datetime import datetime, timezone
from typing import Optional


def parse_datetime(date_str: str) -> Optional[datetime]:
    """
    Parse a datetime string into a datetime object.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Parsed datetime object or None if parsing fails
    """
    if not date_str:
        return None
    
    # Common datetime formats to try
    formats = [
        '%Y-%m-%dT%H:%M:%S.%fZ',      # ISO format with microseconds and Z
        '%Y-%m-%dT%H:%M:%SZ',         # ISO format with Z
        '%Y-%m-%dT%H:%M:%S.%f',       # ISO format with microseconds
        '%Y-%m-%dT%H:%M:%S',          # ISO format
        '%Y-%m-%d %H:%M:%S',          # Standard format
        '%Y-%m-%d',                   # Date only
        '%m/%d/%Y',                   # US format
        '%d/%m/%Y',                   # European format
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            
            # If no timezone info, assume UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            return dt
            
        except ValueError:
            continue
    
    return None


def format_datetime(dt: datetime, format_type: str = 'iso') -> str:
    """
    Format a datetime object to string.
    
    Args:
        dt: Datetime object to format
        format_type: Format type ('iso', 'human', 'date_only')
        
    Returns:
        Formatted datetime string
    """
    if not dt:
        return ""
    
    if format_type == 'iso':
        return dt.isoformat()
    elif format_type == 'human':
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    elif format_type == 'date_only':
        return dt.strftime('%Y-%m-%d')
    else:
        return dt.isoformat()


def is_valid_date(date_str: str) -> bool:
    """
    Check if a date string is valid.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid, False otherwise
    """
    return parse_datetime(date_str) is not None


def get_current_utc() -> datetime:
    """
    Get current UTC datetime.
    
    Returns:
        Current UTC datetime
    """
    return datetime.now(timezone.utc)


def is_overdue(due_date: Optional[datetime]) -> bool:
    """
    Check if a task is overdue.
    
    Args:
        due_date: Task due date
        
    Returns:
        True if overdue, False otherwise
    """
    if not due_date:
        return False
    
    return due_date < get_current_utc()


def days_until_due(due_date: Optional[datetime]) -> Optional[int]:
    """
    Calculate days until due date.
    
    Args:
        due_date: Task due date
        
    Returns:
        Number of days until due (negative if overdue), None if no due date
    """
    if not due_date:
        return None
    
    delta = due_date - get_current_utc()
    return delta.days


def format_relative_time(dt: datetime) -> str:
    """
    Format datetime as relative time (e.g., "2 hours ago").
    
    Args:
        dt: Datetime to format
        
    Returns:
        Relative time string
    """
    now = get_current_utc()
    delta = now - dt
    
    if delta.days > 0:
        return f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
    elif delta.seconds > 3600:
        hours = delta.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif delta.seconds > 60:
        minutes = delta.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "just now"