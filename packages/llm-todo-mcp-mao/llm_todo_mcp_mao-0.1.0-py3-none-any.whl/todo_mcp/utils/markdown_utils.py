"""
Markdown processing utilities for the Todo MCP system.

This module provides utility functions for markdown processing,
including slugification, content formatting, and YAML frontmatter parsing.
"""

import re
from typing import Any, Dict, Optional, Tuple

import yaml


def slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug.
    
    Args:
        text: Input text to slugify
        
    Returns:
        Slugified text suitable for filenames
    """
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().strip()
    
    # Remove special characters except hyphens and underscores
    slug = re.sub(r'[^\w\s-]', '', slug)
    
    # Replace spaces and multiple hyphens with single hyphen
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug


def format_task_content(content: str) -> str:
    """
    Format task content with proper markdown structure.
    
    Args:
        content: Raw task content
        
    Returns:
        Formatted markdown content
    """
    if not content:
        return ""
    
    # Normalize line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove excessive whitespace
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Ensure proper spacing around headers
    content = re.sub(r'\n(#{1,6}\s)', r'\n\n\1', content)
    content = re.sub(r'(#{1,6}.*)\n([^\n#])', r'\1\n\n\2', content)
    
    return content.strip()


def parse_yaml_frontmatter(content: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Parse YAML frontmatter from markdown content.
    
    Args:
        content: Markdown content with potential frontmatter
        
    Returns:
        Tuple of (frontmatter_dict, body_content)
    """
    # Pattern to match YAML frontmatter
    frontmatter_pattern = re.compile(
        r'^---\s*\n(.*?)\n---\s*\n(.*)',
        re.DOTALL | re.MULTILINE
    )
    
    match = frontmatter_pattern.match(content.strip())
    
    if match:
        try:
            frontmatter_yaml = match.group(1)
            body = match.group(2)
            
            # Parse YAML
            frontmatter = yaml.safe_load(frontmatter_yaml)
            
            return frontmatter, body
            
        except yaml.YAMLError:
            # If YAML parsing fails, treat as regular content
            return None, content
    
    # No frontmatter found
    return None, content


def extract_task_id_from_filename(filename: str) -> Optional[str]:
    """
    Extract task ID from a markdown filename.
    
    Args:
        filename: Markdown filename (e.g., "001_setup-project.md")
        
    Returns:
        Task ID if extractable, None otherwise
    """
    # Remove .md extension
    name = filename.replace('.md', '')
    
    # Pattern to match task ID at the beginning
    match = re.match(r'^(\w+)_', name)
    
    if match:
        return match.group(1)
    
    # Fallback: use entire filename without extension as ID
    return name if name else None


def generate_task_filename(task_id: str, title: str) -> str:
    """
    Generate a filename for a task.
    
    Args:
        task_id: Task identifier
        title: Task title
        
    Returns:
        Generated filename
    """
    slug = slugify(title)
    return f"{task_id}_{slug}.md"


def validate_markdown_structure(content: str) -> bool:
    """
    Validate that markdown content has proper structure.
    
    Args:
        content: Markdown content to validate
        
    Returns:
        True if structure is valid, False otherwise
    """
    # Check for frontmatter
    if not content.strip().startswith('---'):
        return False
    
    # Check for closing frontmatter delimiter
    if content.count('---') < 2:
        return False
    
    return True