"""
Markdown format writer for task files.

This module handles writing Task objects to markdown files with YAML
frontmatter and structured content formatting.
"""

import logging
from typing import Any, Dict

import yaml

from ..models.task import Task


class MarkdownWriter:
    """
    Writer for markdown task files with YAML frontmatter.
    
    This class handles the conversion of Task objects into properly
    formatted markdown files with structured frontmatter.
    """
    
    def __init__(self):
        """Initialize the markdown writer."""
        self.logger = logging.getLogger(__name__)
    
    def write_task_file(self, task: Task) -> str:
        """
        Convert a Task object to markdown file content.
        
        Args:
            task: Task object to convert
            
        Returns:
            Formatted markdown content with YAML frontmatter
        """
        try:
            # Prepare frontmatter data using Pydantic serialization
            frontmatter_data = self._prepare_frontmatter(task)
            
            # Generate YAML frontmatter with proper formatting
            frontmatter = yaml.dump(
                frontmatter_data,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                indent=2,
                width=80
            )
            
            # Format the task description content
            formatted_description = self.format_task_content(task)
            
            # Combine frontmatter and content
            if formatted_description.strip():
                content = f"---\n{frontmatter}---\n\n{formatted_description}"
            else:
                content = f"---\n{frontmatter}---\n"
            
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to write task file: {e}")
            raise
    
    def _prepare_frontmatter(self, task: Task) -> Dict[str, Any]:
        """
        Prepare frontmatter data from Task object using Pydantic serialization.
        
        Args:
            task: Task object
            
        Returns:
            Dictionary suitable for YAML frontmatter
        """
        # Use Pydantic's model_dump method for proper serialization
        task_dict = task.model_dump(mode='json', exclude={'description'})
        
        # Convert datetime objects to ISO format strings for YAML
        for field in ['created_at', 'updated_at', 'due_date']:
            if field in task_dict and task_dict[field] is not None:
                if hasattr(task_dict[field], 'isoformat'):
                    task_dict[field] = task_dict[field].isoformat()
        
        # Ensure empty lists and None values are handled properly
        frontmatter = {}
        for key, value in task_dict.items():
            if value is not None:
                if isinstance(value, list) and len(value) == 0:
                    # Include empty lists for clarity
                    frontmatter[key] = value
                elif isinstance(value, dict) and len(value) == 0:
                    # Include empty dicts for clarity
                    frontmatter[key] = value
                else:
                    frontmatter[key] = value
        
        return frontmatter
    
    def format_task_content(self, task: Task) -> str:
        """
        Format task description content with proper markdown structure.
        
        Args:
            task: Task object
            
        Returns:
            Formatted markdown content
        """
        if not task.description:
            return ""
        
        content = task.description.strip()
        
        # Ensure proper line endings for markdown
        if content:
            # Normalize line endings
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            
            # Ensure content ends with a single newline if it doesn't already
            if not content.endswith('\n'):
                content += '\n'
        
        return content
    
    def write_human_readable_format(self, task: Task) -> str:
        """
        Generate a human-readable markdown format that follows design specifications.
        
        Args:
            task: Task object to format
            
        Returns:
            Human-readable markdown content
        """
        try:
            # Use the standard write method but ensure human readability
            content = self.write_task_file(task)
            
            # Additional formatting for human readability could be added here
            # For now, the YAML frontmatter with proper indentation and the
            # markdown content should be sufficiently human-readable
            
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to write human-readable format: {e}")
            raise
    
    def serialize_task_data(self, task: Task) -> Dict[str, Any]:
        """
        Serialize task data using Pydantic's serialization methods.
        
        Args:
            task: Task object to serialize
            
        Returns:
            Serialized task data dictionary
        """
        try:
            # Use Pydantic's model_dump for proper serialization
            return task.model_dump(mode='json')
            
        except Exception as e:
            self.logger.error(f"Failed to serialize task data: {e}")
            raise