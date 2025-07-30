"""
Core task management service for the Todo MCP system.

This module provides the main business logic for task operations,
including CRUD operations, validation, and coordination with storage.
"""

import logging
import re
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from ..config import TodoConfig
from ..models.task import Task
from ..models.status import TaskStatus, Priority, validate_status_transition, StatusTransitionError
from ..models.filters import TaskFilter, TaskSearchResult
from ..storage.file_manager import FileManager
from ..storage.markdown_parser import MarkdownParser, MarkdownParseError
from ..storage.markdown_writer import MarkdownWriter


class TaskServiceError(Exception):
    """Base exception for task service errors."""
    pass


class TaskNotFoundError(TaskServiceError):
    """Exception raised when a task is not found."""
    pass


class TaskValidationError(TaskServiceError):
    """Exception raised when task validation fails."""
    pass


class TaskService:
    """
    Core service for task management operations.
    
    This service handles all task-related business logic, including
    CRUD operations, validation, and coordination with the storage layer.
    """
    
    def __init__(self, config: TodoConfig):
        """
        Initialize the task service.
        
        Args:
            config: Configuration settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.file_manager = FileManager(config)
        self.markdown_parser = MarkdownParser()
        self.markdown_writer = MarkdownWriter()
        self._task_cache: Dict[str, Task] = {}
        self._cache_dirty = True
    
    async def initialize(self) -> None:
        """Initialize the service and load existing tasks."""
        self.logger.info("Initializing task service")
        await self.file_manager.initialize()
        await self._load_tasks()
    
    async def cleanup(self) -> None:
        """Cleanup service resources."""
        self.logger.info("Cleaning up task service")
        await self.file_manager.cleanup()
        self._task_cache.clear()
    
    async def _load_tasks(self) -> None:
        """Load all tasks from storage into cache."""
        self.logger.debug("Loading tasks from storage")
        
        try:
            task_ids = await self.file_manager.list_task_files()
            loaded_count = 0
            
            for task_id in task_ids:
                try:
                    content = await self.file_manager.read_task_file(task_id)
                    if content:
                        task = self.markdown_parser.parse_task_file(content)
                        self._task_cache[task.id] = task
                        loaded_count += 1
                except (MarkdownParseError, ValidationError) as e:
                    self.logger.error(f"Failed to load task {task_id}: {e}")
                    continue
            
            self.logger.info(f"Loaded {loaded_count} tasks from storage")
            self._cache_dirty = False
            
        except Exception as e:
            self.logger.error(f"Failed to load tasks: {e}")
            raise TaskServiceError(f"Failed to initialize task service: {e}")
    
    def _generate_task_id(self) -> str:
        """Generate a unique task ID."""
        return str(uuid.uuid4())
    
    async def create_task(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        tags: Optional[List[str]] = None,
        parent_id: Optional[str] = None,
        due_date: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """
        Create a new task.
        
        Args:
            title: Task title
            description: Task description
            priority: Task priority
            tags: Task tags
            parent_id: Parent task ID for hierarchy
            due_date: Task due date
            metadata: Additional task metadata
            
        Returns:
            Created task
            
        Raises:
            TaskValidationError: If task validation fails
            TaskServiceError: If task creation fails
        """
        try:
            # Validate parent task exists if specified
            if parent_id:
                parent_task = await self.get_task(parent_id)
                if not parent_task:
                    raise TaskValidationError(f"Parent task not found: {parent_id}")
            
            # Generate unique task ID
            task_id = self._generate_task_id()
            
            # Prepare task data with Pydantic validation
            task_data = {
                'id': task_id,
                'title': title,
                'description': description,
                'status': TaskStatus.PENDING,
                'priority': priority,
                'tags': tags or [],
                'parent_id': parent_id,
                'child_ids': [],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'due_date': due_date,
                'tool_calls': [],
                'metadata': metadata or {},
            }
            
            # Create Task object with Pydantic validation
            task = Task(**task_data)
            
            # Save to storage
            content = self.markdown_writer.write_task_file(task)
            success = await self.file_manager.write_task_file(task_id, content)
            
            if not success:
                raise TaskServiceError(f"Failed to save task to storage: {task_id}")
            
            # Update cache
            self._task_cache[task_id] = task
            
            # Update parent task if specified
            if parent_id:
                await self._add_child_to_parent(parent_id, task_id)
            
            self.logger.info(f"Created task: {task_id} - {title}")
            return task
            
        except ValidationError as e:
            self.logger.error(f"Task validation failed: {e}")
            raise TaskValidationError(f"Task validation failed: {e}")
        except (TaskValidationError, TaskServiceError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating task: {e}")
            raise TaskServiceError(f"Failed to create task: {e}")
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task if found, None otherwise
        """
        try:
            # Check cache first
            if task_id in self._task_cache:
                return self._task_cache[task_id]
            
            # Try to load from storage
            content = await self.file_manager.read_task_file(task_id)
            if content:
                task = self.markdown_parser.parse_task_file(content)
                self._task_cache[task_id] = task
                return task
            
            return None
            
        except (MarkdownParseError, ValidationError) as e:
            self.logger.error(f"Failed to parse task {task_id}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving task {task_id}: {e}")
            return None
    
    async def update_task(self, task_id: str, **updates) -> Optional[Task]:
        """
        Update a task.
        
        Args:
            task_id: Task identifier
            **updates: Fields to update
            
        Returns:
            Updated task if found, None otherwise
            
        Raises:
            TaskValidationError: If validation fails
            TaskServiceError: If update fails
        """
        try:
            # Get existing task
            task = await self.get_task(task_id)
            if not task:
                return None
            
            # Create backup before update
            await self.file_manager.backup_task_file(task_id)
            
            # Prepare updated data using Pydantic's model_dump
            task_data = task.model_dump()
            
            # Apply updates
            for field, value in updates.items():
                if hasattr(task, field):
                    task_data[field] = value
                else:
                    self.logger.warning(f"Unknown field in update: {field}")
            
            # Update timestamp
            task_data['updated_at'] = datetime.utcnow()
            
            # Validate parent task if being updated
            if 'parent_id' in updates and updates['parent_id']:
                parent_task = await self.get_task(updates['parent_id'])
                if not parent_task:
                    raise TaskValidationError(f"Parent task not found: {updates['parent_id']}")
            
            # Create updated Task object with Pydantic validation
            updated_task = Task(**task_data)
            
            # Save to storage
            content = self.markdown_writer.write_task_file(updated_task)
            success = await self.file_manager.write_task_file(task_id, content)
            
            if not success:
                raise TaskServiceError(f"Failed to save updated task: {task_id}")
            
            # Update cache
            self._task_cache[task_id] = updated_task
            
            # Handle parent relationship changes
            if 'parent_id' in updates:
                await self._handle_parent_change(task, updated_task)
            
            self.logger.info(f"Updated task: {task_id}")
            return updated_task
            
        except ValidationError as e:
            self.logger.error(f"Task validation failed during update: {e}")
            raise TaskValidationError(f"Task validation failed: {e}")
        except (TaskValidationError, TaskServiceError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error updating task {task_id}: {e}")
            raise TaskServiceError(f"Failed to update task: {e}")
    
    async def delete_task(self, task_id: str, cascade: bool = False) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: Task identifier
            cascade: If True, delete child tasks as well
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            TaskServiceError: If deletion fails
        """
        try:
            # Get task to check if it exists
            task = await self.get_task(task_id)
            if not task:
                return False
            
            # Create backup before deletion
            await self.file_manager.backup_task_file(task_id)
            
            # Handle child tasks
            if task.child_ids:
                if cascade:
                    # Delete all child tasks recursively
                    for child_id in task.child_ids.copy():
                        await self.delete_task(child_id, cascade=True)
                else:
                    # Remove parent reference from child tasks
                    for child_id in task.child_ids:
                        child_task = await self.get_task(child_id)
                        if child_task and child_task.parent_id == task_id:
                            await self.update_task(child_id, parent_id=None)
            
            # Remove from parent's child list
            if task.parent_id:
                await self._remove_child_from_parent(task.parent_id, task_id)
            
            # Delete from storage
            success = await self.file_manager.delete_task_file(task_id)
            
            if not success:
                raise TaskServiceError(f"Failed to delete task from storage: {task_id}")
            
            # Remove from cache
            self._task_cache.pop(task_id, None)
            
            self.logger.info(f"Deleted task: {task_id}")
            return True
            
        except TaskServiceError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error deleting task {task_id}: {e}")
            raise TaskServiceError(f"Failed to delete task: {e}")
    
    async def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[Priority] = None,
        tags: Optional[List[str]] = None,
        parent_id: Optional[str] = None,
        include_completed: bool = True,
    ) -> List[Task]:
        """
        List tasks with optional filtering.
        
        Args:
            status: Filter by status
            priority: Filter by priority
            tags: Filter by tags
            parent_id: Filter by parent task ID
            include_completed: Include completed tasks
            
        Returns:
            List of matching tasks
        """
        try:
            # Ensure cache is loaded
            if self._cache_dirty:
                await self._load_tasks()
            
            tasks = list(self._task_cache.values())
            
            # Apply filters
            if status is not None:
                tasks = [t for t in tasks if t.status == status]
            
            if priority is not None:
                tasks = [t for t in tasks if t.priority == priority]
            
            if tags:
                tasks = [t for t in tasks if any(tag in t.tags for tag in tags)]
            
            if parent_id is not None:
                tasks = [t for t in tasks if t.parent_id == parent_id]
            
            if not include_completed:
                tasks = [t for t in tasks if t.status != TaskStatus.COMPLETED]
            
            # Sort by creation date (newest first)
            tasks.sort(key=lambda t: t.created_at, reverse=True)
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Error listing tasks: {e}")
            return []
    
    async def get_task_count(self) -> int:
        """
        Get total number of tasks.
        
        Returns:
            Total task count
        """
        try:
            if self._cache_dirty:
                await self._load_tasks()
            return len(self._task_cache)
        except Exception as e:
            self.logger.error(f"Error getting task count: {e}")
            return 0
    
    async def _add_child_to_parent(self, parent_id: str, child_id: str) -> None:
        """Add child task to parent's child list."""
        parent_task = await self.get_task(parent_id)
        if parent_task and child_id not in parent_task.child_ids:
            parent_task.add_child(child_id)
            content = self.markdown_writer.write_task_file(parent_task)
            await self.file_manager.write_task_file(parent_id, content)
            self._task_cache[parent_id] = parent_task
    
    async def _remove_child_from_parent(self, parent_id: str, child_id: str) -> None:
        """Remove child task from parent's child list."""
        parent_task = await self.get_task(parent_id)
        if parent_task and child_id in parent_task.child_ids:
            parent_task.remove_child(child_id)
            content = self.markdown_writer.write_task_file(parent_task)
            await self.file_manager.write_task_file(parent_id, content)
            self._task_cache[parent_id] = parent_task
    
    async def _handle_parent_change(self, old_task: Task, new_task: Task) -> None:
        """Handle parent relationship changes during task update."""
        old_parent = old_task.parent_id
        new_parent = new_task.parent_id
        
        if old_parent != new_parent:
            # Remove from old parent
            if old_parent:
                await self._remove_child_from_parent(old_parent, new_task.id)
            
            # Add to new parent
            if new_parent:
                await self._add_child_to_parent(new_parent, new_task.id)
    
    async def refresh_cache(self) -> None:
        """Refresh the task cache from storage."""
        self.logger.info("Refreshing task cache")
        self._task_cache.clear()
        self._cache_dirty = True
        await self._load_tasks()
    
    async def check_external_changes(self) -> List[str]:
        """
        Check for external file changes and reload affected tasks.
        
        Returns:
            List of task IDs that were reloaded
        """
        try:
            changed_task_ids = self.file_manager.check_file_changes()
            reloaded_tasks = []
            
            for task_id in changed_task_ids:
                try:
                    content = await self.file_manager.read_task_file(task_id)
                    if content:
                        task = self.markdown_parser.parse_task_file(content)
                        self._task_cache[task.id] = task
                        reloaded_tasks.append(task_id)
                        self.logger.info(f"Reloaded externally modified task: {task_id}")
                    else:
                        # File was deleted externally
                        self._task_cache.pop(task_id, None)
                        reloaded_tasks.append(task_id)
                        self.logger.info(f"Removed externally deleted task: {task_id}")
                except (MarkdownParseError, ValidationError) as e:
                    self.logger.error(f"Failed to reload task {task_id}: {e}")
            
            return reloaded_tasks
            
        except Exception as e:
            self.logger.error(f"Error checking external changes: {e}")
            return []
    
    async def filter_tasks(self, task_filter: TaskFilter) -> TaskSearchResult:
        """
        Filter tasks using advanced criteria with Pydantic validation.
        
        Args:
            task_filter: TaskFilter model with filtering criteria
            
        Returns:
            TaskSearchResult with filtered tasks and metadata
            
        Raises:
            TaskServiceError: If filtering fails
        """
        try:
            start_time = time.time()
            
            # Ensure cache is loaded
            if self._cache_dirty:
                await self._load_tasks()
            
            # Start with all tasks
            tasks = list(self._task_cache.values())
            original_count = len(tasks)
            
            # Apply filters
            tasks = self._apply_status_filter(tasks, task_filter)
            tasks = self._apply_priority_filter(tasks, task_filter)
            tasks = self._apply_tag_filters(tasks, task_filter)
            tasks = self._apply_hierarchy_filters(tasks, task_filter)
            tasks = self._apply_date_filters(tasks, task_filter)
            tasks = self._apply_text_search(tasks, task_filter)
            tasks = self._apply_completion_filter(tasks, task_filter)
            
            # Get total count before pagination
            total_count = len(tasks)
            
            # Apply sorting
            tasks = self._sort_tasks(tasks, task_filter)
            
            # Apply pagination
            tasks, has_more = self._paginate_tasks(tasks, task_filter)
            
            # Calculate search time
            search_time_ms = (time.time() - start_time) * 1000
            
            # Create result
            result = TaskSearchResult(
                tasks=tasks,
                total_count=total_count,
                filtered_count=len(tasks),
                has_more=has_more,
                offset=task_filter.offset,
                limit=task_filter.limit,
                filter_applied=task_filter,
                search_time_ms=search_time_ms
            )
            
            self.logger.debug(f"Filtered {original_count} tasks to {total_count} results in {search_time_ms:.2f}ms")
            return result
            
        except Exception as e:
            self.logger.error(f"Error filtering tasks: {e}")
            raise TaskServiceError(f"Failed to filter tasks: {e}")
    
    def _apply_status_filter(self, tasks: List[Task], task_filter: TaskFilter) -> List[Task]:
        """Apply status filtering."""
        if not task_filter.status:
            return tasks
        
        return [task for task in tasks if task.status in task_filter.status]
    
    def _apply_priority_filter(self, tasks: List[Task], task_filter: TaskFilter) -> List[Task]:
        """Apply priority filtering."""
        if not task_filter.priority:
            return tasks
        
        return [task for task in tasks if task.priority in task_filter.priority]
    
    def _apply_tag_filters(self, tasks: List[Task], task_filter: TaskFilter) -> List[Task]:
        """Apply tag filtering (any or all match)."""
        if task_filter.tags:
            # Any tag match
            tasks = [
                task for task in tasks 
                if any(tag in task.tags for tag in task_filter.tags)
            ]
        
        if task_filter.tags_all:
            # All tags must match
            tasks = [
                task for task in tasks 
                if all(tag in task.tags for tag in task_filter.tags_all)
            ]
        
        return tasks
    
    def _apply_hierarchy_filters(self, tasks: List[Task], task_filter: TaskFilter) -> List[Task]:
        """Apply hierarchy-based filtering."""
        if task_filter.parent_id is not None:
            tasks = [task for task in tasks if task.parent_id == task_filter.parent_id]
        
        if task_filter.has_parent is not None:
            if task_filter.has_parent:
                tasks = [task for task in tasks if task.parent_id is not None]
            else:
                tasks = [task for task in tasks if task.parent_id is None]
        
        if task_filter.has_children is not None:
            if task_filter.has_children:
                tasks = [task for task in tasks if task.child_ids]
            else:
                tasks = [task for task in tasks if not task.child_ids]
        
        return tasks
    
    def _apply_date_filters(self, tasks: List[Task], task_filter: TaskFilter) -> List[Task]:
        """Apply date-based filtering."""
        if task_filter.created_after:
            tasks = [task for task in tasks if task.created_at >= task_filter.created_after]
        
        if task_filter.created_before:
            tasks = [task for task in tasks if task.created_at <= task_filter.created_before]
        
        if task_filter.updated_after:
            tasks = [task for task in tasks if task.updated_at >= task_filter.updated_after]
        
        if task_filter.updated_before:
            tasks = [task for task in tasks if task.updated_at <= task_filter.updated_before]
        
        if task_filter.due_after:
            tasks = [task for task in tasks if task.due_date and task.due_date >= task_filter.due_after]
        
        if task_filter.due_before:
            tasks = [task for task in tasks if task.due_date and task.due_date <= task_filter.due_before]
        
        if task_filter.has_due_date is not None:
            if task_filter.has_due_date:
                tasks = [task for task in tasks if task.due_date is not None]
            else:
                tasks = [task for task in tasks if task.due_date is None]
        
        return tasks
    
    def _apply_text_search(self, tasks: List[Task], task_filter: TaskFilter) -> List[Task]:
        """Apply text-based search filtering."""
        if task_filter.search_text:
            search_term = task_filter.search_text.lower()
            tasks = [
                task for task in tasks 
                if (search_term in task.title.lower() or 
                    search_term in task.description.lower())
            ]
        
        if task_filter.title_contains:
            search_term = task_filter.title_contains.lower()
            tasks = [task for task in tasks if search_term in task.title.lower()]
        
        if task_filter.description_contains:
            search_term = task_filter.description_contains.lower()
            tasks = [task for task in tasks if search_term in task.description.lower()]
        
        return tasks
    
    def _apply_completion_filter(self, tasks: List[Task], task_filter: TaskFilter) -> List[Task]:
        """Apply completion status filtering."""
        if not task_filter.include_completed:
            tasks = [task for task in tasks if task.status != TaskStatus.COMPLETED]
        
        return tasks
    
    def _sort_tasks(self, tasks: List[Task], task_filter: TaskFilter) -> List[Task]:
        """Sort tasks based on filter criteria."""
        sort_field = task_filter.sort_by
        reverse = task_filter.sort_desc
        
        try:
            if sort_field == 'created_at':
                tasks.sort(key=lambda t: t.created_at, reverse=reverse)
            elif sort_field == 'updated_at':
                tasks.sort(key=lambda t: t.updated_at, reverse=reverse)
            elif sort_field == 'due_date':
                # Handle None values for due_date
                tasks.sort(key=lambda t: t.due_date or datetime.min, reverse=reverse)
            elif sort_field == 'title':
                tasks.sort(key=lambda t: t.title.lower(), reverse=reverse)
            elif sort_field == 'status':
                tasks.sort(key=lambda t: t.status.value, reverse=reverse)
            elif sort_field == 'priority':
                tasks.sort(key=lambda t: t.priority.value, reverse=reverse)
            elif sort_field == 'id':
                tasks.sort(key=lambda t: t.id, reverse=reverse)
            
        except Exception as e:
            self.logger.warning(f"Failed to sort by {sort_field}: {e}")
            # Fall back to default sorting
            tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        return tasks
    
    def _paginate_tasks(self, tasks: List[Task], task_filter: TaskFilter) -> tuple[List[Task], bool]:
        """Apply pagination to task list."""
        offset = task_filter.offset
        limit = task_filter.limit
        
        if offset >= len(tasks):
            return [], False
        
        if limit is None:
            return tasks[offset:], False
        
        end_index = offset + limit
        paginated_tasks = tasks[offset:end_index]
        has_more = end_index < len(tasks)
        
        return paginated_tasks, has_more
    
    async def search_tasks(self, search_text: str, **kwargs) -> TaskSearchResult:
        """
        Simple text search across tasks.
        
        Args:
            search_text: Text to search for
            **kwargs: Additional filter parameters
            
        Returns:
            TaskSearchResult with matching tasks
        """
        try:
            # Create filter with search text
            filter_data = {'search_text': search_text, **kwargs}
            task_filter = TaskFilter(**filter_data)
            
            return await self.filter_tasks(task_filter)
            
        except ValidationError as e:
            self.logger.error(f"Invalid search parameters: {e}")
            raise TaskValidationError(f"Invalid search parameters: {e}")
        except Exception as e:
            self.logger.error(f"Error searching tasks: {e}")
            raise TaskServiceError(f"Failed to search tasks: {e}")
    
    async def get_tasks_by_status(self, status: TaskStatus, **kwargs) -> List[Task]:
        """
        Get tasks filtered by status.
        
        Args:
            status: Task status to filter by
            **kwargs: Additional filter parameters
            
        Returns:
            List of tasks with the specified status
        """
        try:
            filter_data = {'status': [status], **kwargs}
            task_filter = TaskFilter(**filter_data)
            
            result = await self.filter_tasks(task_filter)
            return result.tasks
            
        except Exception as e:
            self.logger.error(f"Error getting tasks by status {status}: {e}")
            return []
    
    async def get_tasks_by_priority(self, priority: Priority, **kwargs) -> List[Task]:
        """
        Get tasks filtered by priority.
        
        Args:
            priority: Task priority to filter by
            **kwargs: Additional filter parameters
            
        Returns:
            List of tasks with the specified priority
        """
        try:
            filter_data = {'priority': [priority], **kwargs}
            task_filter = TaskFilter(**filter_data)
            
            result = await self.filter_tasks(task_filter)
            return result.tasks
            
        except Exception as e:
            self.logger.error(f"Error getting tasks by priority {priority}: {e}")
            return []
    
    async def get_tasks_by_tags(self, tags: List[str], match_all: bool = False, **kwargs) -> List[Task]:
        """
        Get tasks filtered by tags.
        
        Args:
            tags: List of tags to filter by
            match_all: If True, task must have all tags; if False, any tag matches
            **kwargs: Additional filter parameters
            
        Returns:
            List of tasks matching the tag criteria
        """
        try:
            if match_all:
                filter_data = {'tags_all': tags, **kwargs}
            else:
                filter_data = {'tags': tags, **kwargs}
            
            task_filter = TaskFilter(**filter_data)
            result = await self.filter_tasks(task_filter)
            return result.tasks
            
        except Exception as e:
            self.logger.error(f"Error getting tasks by tags {tags}: {e}")
            return []
    
    async def get_overdue_tasks(self, **kwargs) -> List[Task]:
        """
        Get tasks that are overdue.
        
        Args:
            **kwargs: Additional filter parameters
            
        Returns:
            List of overdue tasks
        """
        try:
            now = datetime.utcnow()
            filter_data = {
                'due_before': now,
                'has_due_date': True,
                'status': [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED],
                **kwargs
            }
            
            task_filter = TaskFilter(**filter_data)
            result = await self.filter_tasks(task_filter)
            return result.tasks
            
        except Exception as e:
            self.logger.error(f"Error getting overdue tasks: {e}")
            return []
    
    async def get_task_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive task statistics.
        
        Returns:
            Dictionary with various task statistics
        """
        try:
            if self._cache_dirty:
                await self._load_tasks()
            
            tasks = list(self._task_cache.values())
            total_count = len(tasks)
            
            if total_count == 0:
                return {
                    'total_tasks': 0,
                    'by_status': {},
                    'by_priority': {},
                    'with_due_dates': 0,
                    'overdue': 0,
                    'completed_today': 0,
                    'created_today': 0,
                }
            
            # Count by status
            status_counts = {}
            for status in TaskStatus:
                status_counts[status.value] = len([t for t in tasks if t.status == status])
            
            # Count by priority
            priority_counts = {}
            for priority in Priority:
                priority_counts[priority.name.lower()] = len([t for t in tasks if t.priority == priority])
            
            # Date-based statistics
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            with_due_dates = len([t for t in tasks if t.due_date is not None])
            overdue = len([
                t for t in tasks 
                if t.due_date and t.due_date < now and t.status != TaskStatus.COMPLETED
            ])
            completed_today = len([
                t for t in tasks 
                if t.status == TaskStatus.COMPLETED and t.updated_at >= today_start
            ])
            created_today = len([
                t for t in tasks 
                if t.created_at >= today_start
            ])
            
            return {
                'total_tasks': total_count,
                'by_status': status_counts,
                'by_priority': priority_counts,
                'with_due_dates': with_due_dates,
                'overdue': overdue,
                'completed_today': completed_today,
                'created_today': created_today,
                'cache_size': len(self._task_cache),
                'cache_dirty': self._cache_dirty,
            }
            
        except Exception as e:
            self.logger.error(f"Error getting task statistics: {e}")
            return {'error': str(e)}
    
    async def update_task_status(
        self, 
        task_id: str, 
        new_status: TaskStatus, 
        validate_transition: bool = True,
        audit_log: bool = True
    ) -> Optional[Task]:
        """
        Update task status with validation and audit logging.
        
        Args:
            task_id: Task identifier
            new_status: New status to set
            validate_transition: Whether to validate status transition
            audit_log: Whether to log the status change
            
        Returns:
            Updated task if successful, None if task not found
            
        Raises:
            TaskValidationError: If status transition is invalid
            TaskServiceError: If update fails
        """
        try:
            # Get existing task
            task = await self.get_task(task_id)
            if not task:
                return None
            
            old_status = task.status
            
            # Validate status transition if requested
            if validate_transition and old_status != new_status:
                try:
                    validate_status_transition(old_status, new_status)
                except StatusTransitionError as e:
                    raise TaskValidationError(str(e))
            
            # Create audit log entry if requested
            audit_entry = None
            if audit_log:
                audit_entry = {
                    'action': 'status_change',
                    'timestamp': datetime.utcnow().isoformat(),
                    'old_status': old_status.value,
                    'new_status': new_status.value,
                    'task_id': task_id,
                    'task_title': task.title
                }
            
            # Update the task
            updated_task = await self.update_task(task_id, status=new_status)
            
            if updated_task and audit_entry:
                # Add audit entry to task metadata
                if 'audit_log' not in updated_task.metadata:
                    updated_task.metadata['audit_log'] = []
                updated_task.metadata['audit_log'].append(audit_entry)
                
                # Save the updated task with audit log
                content = self.markdown_writer.write_task_file(updated_task)
                await self.file_manager.write_task_file(task_id, content)
                self._task_cache[task_id] = updated_task
                
                self.logger.info(f"Status changed for task {task_id}: {old_status.value} -> {new_status.value}")
            
            return updated_task
            
        except (TaskValidationError, TaskServiceError):
            raise
        except Exception as e:
            self.logger.error(f"Error updating task status {task_id}: {e}")
            raise TaskServiceError(f"Failed to update task status: {e}")
    
    async def bulk_update_status(
        self, 
        task_ids: List[str], 
        new_status: TaskStatus,
        validate_transitions: bool = True,
        audit_log: bool = True
    ) -> Dict[str, Any]:
        """
        Update status for multiple tasks atomically.
        
        Args:
            task_ids: List of task identifiers
            new_status: New status to set for all tasks
            validate_transitions: Whether to validate status transitions
            audit_log: Whether to log status changes
            
        Returns:
            Dictionary with success/failure results
        """
        results = {
            'successful': [],
            'failed': [],
            'total_requested': len(task_ids),
            'total_successful': 0,
            'total_failed': 0,
            'errors': []
        }
        
        try:
            # First pass: validate all transitions if requested
            if validate_transitions:
                validation_errors = []
                for task_id in task_ids:
                    task = await self.get_task(task_id)
                    if not task:
                        validation_errors.append(f"Task not found: {task_id}")
                        continue
                    
                    if task.status != new_status:
                        try:
                            validate_status_transition(task.status, new_status)
                        except StatusTransitionError as e:
                            validation_errors.append(f"Task {task_id}: {str(e)}")
                
                if validation_errors:
                    results['errors'] = validation_errors
                    results['total_failed'] = len(task_ids)
                    results['failed'] = task_ids
                    return results
            
            # Second pass: perform updates
            for task_id in task_ids:
                try:
                    updated_task = await self.update_task_status(
                        task_id, 
                        new_status, 
                        validate_transition=False,  # Already validated above
                        audit_log=audit_log
                    )
                    
                    if updated_task:
                        results['successful'].append(task_id)
                    else:
                        results['failed'].append(task_id)
                        results['errors'].append(f"Task not found: {task_id}")
                        
                except Exception as e:
                    results['failed'].append(task_id)
                    results['errors'].append(f"Task {task_id}: {str(e)}")
            
            results['total_successful'] = len(results['successful'])
            results['total_failed'] = len(results['failed'])
            
            self.logger.info(
                f"Bulk status update completed: {results['total_successful']}/{results['total_requested']} successful"
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in bulk status update: {e}")
            results['errors'].append(f"Bulk operation failed: {str(e)}")
            results['total_failed'] = len(task_ids)
            results['failed'] = task_ids
            return results
    
    async def get_status_transition_history(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Get status transition history for a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            List of status transition audit entries
        """
        try:
            task = await self.get_task(task_id)
            if not task:
                return []
            
            audit_log = task.metadata.get('audit_log', [])
            
            # Filter for status change entries
            status_changes = [
                entry for entry in audit_log 
                if entry.get('action') == 'status_change'
            ]
            
            # Sort by timestamp (newest first)
            status_changes.sort(
                key=lambda x: x.get('timestamp', ''), 
                reverse=True
            )
            
            return status_changes
            
        except Exception as e:
            self.logger.error(f"Error getting status history for task {task_id}: {e}")
            return []
    
    async def get_tasks_by_status_transition(
        self, 
        from_status: TaskStatus, 
        to_status: TaskStatus,
        days_back: int = 7
    ) -> List[Task]:
        """
        Get tasks that transitioned from one status to another within a time period.
        
        Args:
            from_status: Original status
            to_status: Target status
            days_back: Number of days to look back
            
        Returns:
            List of tasks that made the transition
        """
        try:
            if self._cache_dirty:
                await self._load_tasks()
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            matching_tasks = []
            
            for task in self._task_cache.values():
                audit_log = task.metadata.get('audit_log', [])
                
                for entry in audit_log:
                    if (entry.get('action') == 'status_change' and
                        entry.get('old_status') == from_status.value and
                        entry.get('new_status') == to_status.value):
                        
                        # Check if transition happened within time period
                        try:
                            entry_time = datetime.fromisoformat(entry.get('timestamp', ''))
                            if entry_time >= cutoff_date:
                                matching_tasks.append(task)
                                break  # Only count each task once
                        except ValueError:
                            continue
            
            return matching_tasks
            
        except Exception as e:
            self.logger.error(f"Error getting tasks by status transition: {e}")
            return []
    
    async def validate_bulk_status_transitions(
        self, 
        task_ids: List[str], 
        new_status: TaskStatus
    ) -> Dict[str, Any]:
        """
        Validate status transitions for multiple tasks without updating them.
        
        Args:
            task_ids: List of task identifiers
            new_status: Proposed new status
            
        Returns:
            Validation results with valid/invalid task lists
        """
        results = {
            'valid_transitions': [],
            'invalid_transitions': [],
            'not_found': [],
            'no_change_needed': [],
            'validation_errors': []
        }
        
        try:
            for task_id in task_ids:
                task = await self.get_task(task_id)
                
                if not task:
                    results['not_found'].append(task_id)
                    continue
                
                if task.status == new_status:
                    results['no_change_needed'].append(task_id)
                    continue
                
                try:
                    validate_status_transition(task.status, new_status)
                    results['valid_transitions'].append({
                        'task_id': task_id,
                        'current_status': task.status.value,
                        'new_status': new_status.value
                    })
                except StatusTransitionError as e:
                    results['invalid_transitions'].append({
                        'task_id': task_id,
                        'current_status': task.status.value,
                        'new_status': new_status.value,
                        'error': str(e)
                    })
                    results['validation_errors'].append(f"Task {task_id}: {str(e)}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error validating bulk status transitions: {e}")
            results['validation_errors'].append(f"Validation failed: {str(e)}")
            return results
    
    async def get_status_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive status-related statistics.
        
        Returns:
            Dictionary with status statistics and transition data
        """
        try:
            if self._cache_dirty:
                await self._load_tasks()
            
            tasks = list(self._task_cache.values())
            total_tasks = len(tasks)
            
            if total_tasks == 0:
                return {
                    'total_tasks': 0,
                    'status_counts': {},
                    'recent_transitions': {},
                    'transition_patterns': {}
                }
            
            # Count tasks by status
            status_counts = {}
            for status in TaskStatus:
                status_counts[status.value] = len([t for t in tasks if t.status == status])
            
            # Analyze recent transitions (last 7 days)
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            recent_transitions = {}
            transition_patterns = {}
            
            for task in tasks:
                audit_log = task.metadata.get('audit_log', [])
                
                for entry in audit_log:
                    if entry.get('action') == 'status_change':
                        try:
                            entry_time = datetime.fromisoformat(entry.get('timestamp', ''))
                            if entry_time >= cutoff_date:
                                old_status = entry.get('old_status')
                                new_status = entry.get('new_status')
                                
                                # Count recent transitions
                                transition_key = f"{old_status} -> {new_status}"
                                recent_transitions[transition_key] = recent_transitions.get(transition_key, 0) + 1
                                
                                # Track transition patterns
                                if old_status not in transition_patterns:
                                    transition_patterns[old_status] = {}
                                transition_patterns[old_status][new_status] = \
                                    transition_patterns[old_status].get(new_status, 0) + 1
                                    
                        except ValueError:
                            continue
            
            return {
                'total_tasks': total_tasks,
                'status_counts': status_counts,
                'recent_transitions': recent_transitions,
                'transition_patterns': transition_patterns,
                'status_distribution': {
                    status: round((count / total_tasks) * 100, 2)
                    for status, count in status_counts.items()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting status statistics: {e}")
            return {'error': str(e)}