"""
Tool call record model for tracking agent interactions.

This module defines the ToolCall model for recording and tracking
all tool interactions with tasks.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class ToolCall(BaseModel):
    """
    Model for recording tool calls and agent interactions.
    
    This model tracks all tool calls made against tasks, providing
    an audit trail of agent interactions and system changes.
    """
    
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When the tool was called")
    tool_name: str = Field(..., min_length=1, description="Name of the tool that was called")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters passed to the tool")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Result returned by the tool")
    agent_id: Optional[str] = Field(default=None, description="ID of the agent that made the call")
    success: bool = Field(default=True, description="Whether the tool call was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if call failed")
    duration_ms: Optional[int] = Field(default=None, description="Tool execution duration in milliseconds")

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
        },
    }

    @field_validator('tool_name')
    @classmethod
    def validate_tool_name(cls, v: str) -> str:
        """Validate tool name is not empty and follows proper format."""
        if not v or not v.strip():
            raise ValueError('Tool name cannot be empty')
        
        # Ensure tool name contains only valid characters
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v.strip()):
            raise ValueError('Tool name can only contain letters, numbers, underscores, and hyphens')
        
        return v.strip()

    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: datetime) -> datetime:
        """Validate timestamp format and ensure timezone awareness."""
        if v.tzinfo is None:
            # Assume UTC if no timezone info
            return v.replace(tzinfo=timezone.utc)
        return v

    @field_validator('error_message')
    @classmethod
    def validate_error_message(cls, v: Optional[str]) -> Optional[str]:
        """Validate error message consistency with success flag."""
        if v is not None and v.strip():
            return v.strip()
        return None

    @field_validator('duration_ms')
    @classmethod
    def validate_duration(cls, v: Optional[int]) -> Optional[int]:
        """Validate duration is non-negative."""
        if v is not None and v < 0:
            raise ValueError('Duration cannot be negative')
        return v

    def mark_success(self, result: Optional[Dict[str, Any]] = None, duration_ms: Optional[int] = None) -> None:
        """Mark the tool call as successful."""
        self.success = True
        self.error_message = None
        if result is not None:
            self.result = result
        if duration_ms is not None:
            self.duration_ms = duration_ms

    def mark_failure(self, error_message: str, duration_ms: Optional[int] = None) -> None:
        """Mark the tool call as failed."""
        self.success = False
        self.error_message = error_message
        self.result = None
        if duration_ms is not None:
            self.duration_ms = duration_ms

    def to_audit_string(self) -> str:
        """Generate a human-readable audit log entry."""
        status = "SUCCESS" if self.success else "FAILURE"
        agent_info = f" by {self.agent_id}" if self.agent_id else ""
        duration_info = f" ({self.duration_ms}ms)" if self.duration_ms else ""
        
        if self.success:
            return f"[{self.timestamp.isoformat()}] {status}: {self.tool_name}{agent_info}{duration_info}"
        else:
            return f"[{self.timestamp.isoformat()}] {status}: {self.tool_name}{agent_info}{duration_info} - {self.error_message}"

    def __str__(self) -> str:
        """String representation of the tool call."""
        status = "✓" if self.success else "✗"
        return f"ToolCall({status} {self.tool_name} at {self.timestamp.isoformat()})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"ToolCall(tool_name='{self.tool_name}', "
                f"timestamp='{self.timestamp.isoformat()}', "
                f"success={self.success})")