"""
Markdown format parser for task files.

This module handles parsing of markdown task files with YAML frontmatter
and structured content into Task objects using Pydantic validation.
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml
from pydantic import ValidationError

from ..models.task import Task
from ..models.status import TaskStatus, Priority


class MarkdownParseError(Exception):
    """Exception raised when markdown parsing fails."""
    pass


class MarkdownParser:
    """
    Parser for markdown task files with YAML frontmatter.
    
    This class handles the conversion of markdown files with structured
    frontmatter into Task objects with full Pydantic validation.
    """
    
    def __init__(self):
        """Initialize the markdown parser."""
        self.logger = logging.getLogger(__name__)
        
        # Regex pattern for YAML frontmatter
        self.frontmatter_pattern = re.compile(
            r'^---\s*\n(.*?)\n---\s*\n(.*)',
            re.DOTALL | re.MULTILINE
        )
    
    def parse_task_file(self, content: str) -> Task:
        """
        Parse a markdown task file into a Task object.
        
        Args:
            content: Raw markdown file content
            
        Returns:
            Parsed Task object
            
        Raises:
            MarkdownParseError: If parsing fails
            ValidationError: If Pydantic validation fails
        """
        try:
            frontmatter, body = self._extract_frontmatter(content)
            
            if not frontmatter:
                raise MarkdownParseError("No YAML frontmatter found in task file")
            
            # Parse YAML frontmatter
            try:
                metadata = yaml.safe_load(frontmatter)
            except (yaml.YAMLError, ValueError) as e:
                raise MarkdownParseError(f"Invalid YAML frontmatter: {e}")
            
            if not metadata or not isinstance(metadata, dict):
                raise MarkdownParseError("YAML frontmatter must be a dictionary")
            
            # Prepare task data with body content
            task_data = self._prepare_task_data(metadata, body)
            
            # Create Task object with Pydantic validation
            try:
                return Task(**task_data)
            except ValidationError as e:
                self.logger.error(f"Pydantic validation failed: {e}")
                raise
            
        except (MarkdownParseError, ValidationError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error parsing task file: {e}")
            raise MarkdownParseError(f"Failed to parse task file: {e}")
    
    def _extract_frontmatter(self, content: str) -> Tuple[Optional[str], str]:
        """
        Extract YAML frontmatter and body from markdown content.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Tuple of (frontmatter, body)
        """
        if not content.strip():
            return None, ""
        
        match = self.frontmatter_pattern.match(content.strip())
        
        if match:
            return match.group(1), match.group(2).strip()
        else:
            # No frontmatter, treat entire content as body
            return None, content.strip()
    
    def _prepare_task_data(self, metadata: Dict[str, Any], body: str) -> Dict[str, Any]:
        """
        Prepare task data for Pydantic validation.
        
        Args:
            metadata: Parsed YAML metadata
            body: Markdown body content
            
        Returns:
            Dictionary ready for Task creation
        """
        task_data = metadata.copy()
        
        # Add description from body
        task_data['description'] = body or ""
        
        # Convert string values to appropriate types
        task_data = self._convert_field_types(task_data)
        
        return task_data
    
    def _convert_field_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert string values to appropriate Python types for Pydantic validation.
        
        Args:
            data: Raw task data dictionary
            
        Returns:
            Dictionary with converted types
        """
        converted = data.copy()
        
        # Convert status string to TaskStatus enum - keep as string for Pydantic
        if 'status' in converted and isinstance(converted['status'], str):
            try:
                # Validate the status is valid, but keep as string
                TaskStatus.from_string(converted['status'])
            except ValueError:
                self.logger.warning(f"Invalid status '{converted['status']}', using default")
                converted['status'] = TaskStatus.PENDING.value
        
        # Convert priority string to Priority enum integer value
        if 'priority' in converted and isinstance(converted['priority'], str):
            try:
                priority_enum = Priority.from_string(converted['priority'])
                converted['priority'] = priority_enum.value
            except ValueError:
                self.logger.warning(f"Invalid priority '{converted['priority']}', using default")
                converted['priority'] = Priority.MEDIUM.value
        
        # Convert datetime strings to datetime objects
        for field in ['created_at', 'updated_at', 'due_date']:
            if field in converted:
                if isinstance(converted[field], str):
                    try:
                        converted[field] = datetime.fromisoformat(converted[field].replace('Z', '+00:00'))
                    except ValueError:
                        self.logger.warning(f"Invalid datetime format for {field}: {converted[field]}")
                        if field in ['created_at', 'updated_at']:
                            converted[field] = datetime.utcnow()
                        else:
                            converted[field] = None
                elif isinstance(converted[field], datetime):
                    # Already a datetime object (from YAML parsing)
                    pass
                else:
                    # Handle other types or None
                    if converted[field] is None:
                        pass  # Keep as None
                    else:
                        self.logger.warning(f"Unexpected type for {field}: {type(converted[field])}")
                        if field in ['created_at', 'updated_at']:
                            converted[field] = datetime.utcnow()
                        else:
                            converted[field] = None
        
        # Ensure tags is a list
        if 'tags' in converted:
            if isinstance(converted['tags'], str):
                # Split comma-separated tags
                converted['tags'] = [tag.strip() for tag in converted['tags'].split(',') if tag.strip()]
            elif not isinstance(converted['tags'], list):
                converted['tags'] = []
        
        # Ensure child_ids is a list
        if 'child_ids' in converted:
            if isinstance(converted['child_ids'], str):
                # Split comma-separated IDs
                converted['child_ids'] = [id.strip() for id in converted['child_ids'].split(',') if id.strip()]
            elif not isinstance(converted['child_ids'], list):
                converted['child_ids'] = []
        
        # Ensure tool_calls is a list
        if 'tool_calls' in converted and not isinstance(converted['tool_calls'], list):
            converted['tool_calls'] = []
        
        # Ensure metadata is a dict
        if 'metadata' in converted and not isinstance(converted['metadata'], dict):
            converted['metadata'] = {}
        
        return converted
    
    def validate_task_structure(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate that task metadata has required fields.
        
        Args:
            metadata: Parsed YAML metadata
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['id', 'title']
        
        for field in required_fields:
            if field not in metadata:
                self.logger.error(f"Missing required field: {field}")
                return False
            
            if not metadata[field] or (isinstance(metadata[field], str) and not metadata[field].strip()):
                self.logger.error(f"Required field '{field}' is empty")
                return False
        
        return True
    
    def parse_multiple_tasks(self, content: str) -> List[Task]:
        """
        Parse multiple tasks from a single markdown file.
        
        Args:
            content: Raw markdown content with multiple task sections
            
        Returns:
            List of parsed Task objects
            
        Raises:
            MarkdownParseError: If parsing fails
        """
        # Split content by task separators (e.g., "---" or "# Task")
        task_sections = self._split_task_sections(content)
        
        tasks = []
        for i, section in enumerate(task_sections):
            try:
                task = self.parse_task_file(section)
                tasks.append(task)
            except (MarkdownParseError, ValidationError) as e:
                self.logger.error(f"Failed to parse task section {i + 1}: {e}")
                # Continue parsing other sections
                continue
        
        return tasks
    
    def _split_task_sections(self, content: str) -> List[str]:
        """
        Split content into individual task sections.
        
        Args:
            content: Raw markdown content
            
        Returns:
            List of task section strings
        """
        # For now, assume single task per file
        # This can be extended to support multiple tasks
        return [content] if content.strip() else []