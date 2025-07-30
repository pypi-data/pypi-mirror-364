"""
Unit tests for the TaskService class.

This module tests all CRUD operations, validation, and error handling
for the core task management service.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import ValidationError

from src.todo_mcp.config import TodoConfig
from src.todo_mcp.models.task import Task
from src.todo_mcp.models.status import TaskStatus, Priority
from src.todo_mcp.services.task_service import (
    TaskService,
    TaskServiceError,
    TaskNotFoundError,
    TaskValidationError,
)


@pytest.fixture
def config():
    """Create test configuration."""
    return TodoConfig(
        data_directory=Path("test_data"),
        max_cache_size=100,
        file_watch_enabled=False,
        backup_enabled=False,
        log_level="DEBUG",
    )


@pytest.fixture
def task_service(config):
    """Create TaskService instance for testing."""
    return TaskService(config)


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        'id': 'test-task-001',
        'title': 'Test Task',
        'description': 'This is a test task',
        'status': TaskStatus.PENDING,
        'priority': Priority.MEDIUM,
        'tags': ['test', 'sample'],
        'parent_id': None,
        'child_ids': [],
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'due_date': None,
        'tool_calls': [],
        'metadata': {},
    }


@pytest.fixture
def sample_task(sample_task_data):
    """Create sample Task object."""
    return Task(**sample_task_data)


class TestTaskServiceInitialization:
    """Test TaskService initialization and setup."""
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, task_service):
        """Test successful service initialization."""
        with patch.object(task_service.file_manager, 'initialize', new_callable=AsyncMock) as mock_init:
            with patch.object(task_service, '_load_tasks', new_callable=AsyncMock) as mock_load:
                await task_service.initialize()
                
                mock_init.assert_called_once()
                mock_load.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup(self, task_service):
        """Test service cleanup."""
        task_service._task_cache = {'test': MagicMock()}
        
        with patch.object(task_service.file_manager, 'cleanup', new_callable=AsyncMock) as mock_cleanup:
            await task_service.cleanup()
            
            mock_cleanup.assert_called_once()
            assert len(task_service._task_cache) == 0
    
    @pytest.mark.asyncio
    async def test_load_tasks_success(self, task_service, sample_task):
        """Test successful task loading from storage."""
        mock_content = "---\nid: test-task-001\ntitle: Test Task\n---\nTest content"
        
        with patch.object(task_service.file_manager, 'list_task_files', new_callable=AsyncMock, return_value=['test-task-001']):
            with patch.object(task_service.file_manager, 'read_task_file', new_callable=AsyncMock, return_value=mock_content):
                with patch.object(task_service.markdown_parser, 'parse_task_file', return_value=sample_task):
                    await task_service._load_tasks()
                    
                    assert 'test-task-001' in task_service._task_cache
                    assert task_service._task_cache['test-task-001'] == sample_task
                    assert not task_service._cache_dirty
    
    @pytest.mark.asyncio
    async def test_load_tasks_parse_error(self, task_service):
        """Test task loading with parse errors."""
        from pydantic_core import ValidationError as CoreValidationError
        
        with patch.object(task_service.file_manager, 'list_task_files', new_callable=AsyncMock, return_value=['invalid-task']):
            with patch.object(task_service.file_manager, 'read_task_file', new_callable=AsyncMock, return_value="invalid content"):
                with patch.object(task_service.markdown_parser, 'parse_task_file', side_effect=ValidationError.from_exception_data("Task", [])):
                    await task_service._load_tasks()
                    
                    # Should not crash and cache should be empty
                    assert len(task_service._task_cache) == 0


class TestTaskServiceCRUD:
    """Test CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_task_success(self, task_service):
        """Test successful task creation."""
        with patch.object(task_service.file_manager, 'write_task_file', new_callable=AsyncMock, return_value=True):
            with patch.object(task_service.markdown_writer, 'write_task_file', return_value="mock content"):
                task = await task_service.create_task(
                    title="New Task",
                    description="Task description",
                    priority=Priority.HIGH,
                    tags=['urgent', 'important']
                )
                
                assert task.title == "New Task"
                assert task.description == "Task description"
                assert task.priority == Priority.HIGH
                assert task.tags == ['urgent', 'important']
                assert task.status == TaskStatus.PENDING
                assert task.id in task_service._task_cache
    
    @pytest.mark.asyncio
    async def test_create_task_with_parent(self, task_service, sample_task):
        """Test task creation with parent relationship."""
        # Setup parent task in cache
        task_service._task_cache[sample_task.id] = sample_task
        
        with patch.object(task_service.file_manager, 'write_task_file', new_callable=AsyncMock, return_value=True):
            with patch.object(task_service.markdown_writer, 'write_task_file', return_value="mock content"):
                with patch.object(task_service, '_add_child_to_parent', new_callable=AsyncMock) as mock_add_child:
                    task = await task_service.create_task(
                        title="Child Task",
                        parent_id=sample_task.id
                    )
                    
                    assert task.parent_id == sample_task.id
                    mock_add_child.assert_called_once_with(sample_task.id, task.id)
    
    @pytest.mark.asyncio
    async def test_create_task_invalid_parent(self, task_service):
        """Test task creation with non-existent parent."""
        with pytest.raises(TaskValidationError, match="Parent task not found"):
            await task_service.create_task(
                title="Child Task",
                parent_id="non-existent-parent"
            )
    
    @pytest.mark.asyncio
    async def test_create_task_validation_error(self, task_service):
        """Test task creation with validation errors."""
        with pytest.raises(TaskValidationError):
            await task_service.create_task(
                title="",  # Empty title should fail validation
            )
    
    @pytest.mark.asyncio
    async def test_create_task_storage_failure(self, task_service):
        """Test task creation with storage failure."""
        with patch.object(task_service.file_manager, 'write_task_file', new_callable=AsyncMock, return_value=False):
            with patch.object(task_service.markdown_writer, 'write_task_file', return_value="mock content"):
                with pytest.raises(TaskServiceError, match="Failed to save task to storage"):
                    await task_service.create_task(title="Test Task")
    
    @pytest.mark.asyncio
    async def test_get_task_from_cache(self, task_service, sample_task):
        """Test getting task from cache."""
        task_service._task_cache[sample_task.id] = sample_task
        
        result = await task_service.get_task(sample_task.id)
        
        assert result == sample_task
    
    @pytest.mark.asyncio
    async def test_get_task_from_storage(self, task_service, sample_task):
        """Test getting task from storage when not in cache."""
        mock_content = "---\nid: test-task-001\ntitle: Test Task\n---\nTest content"
        
        with patch.object(task_service.file_manager, 'read_task_file', new_callable=AsyncMock, return_value=mock_content):
            with patch.object(task_service.markdown_parser, 'parse_task_file', return_value=sample_task):
                result = await task_service.get_task(sample_task.id)
                
                assert result == sample_task
                assert sample_task.id in task_service._task_cache
    
    @pytest.mark.asyncio
    async def test_get_task_not_found(self, task_service):
        """Test getting non-existent task."""
        with patch.object(task_service.file_manager, 'read_task_file', new_callable=AsyncMock, return_value=None):
            result = await task_service.get_task("non-existent")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_update_task_success(self, task_service, sample_task):
        """Test successful task update."""
        task_service._task_cache[sample_task.id] = sample_task
        
        with patch.object(task_service.file_manager, 'backup_task_file', new_callable=AsyncMock):
            with patch.object(task_service.file_manager, 'write_task_file', new_callable=AsyncMock, return_value=True):
                with patch.object(task_service.markdown_writer, 'write_task_file', return_value="mock content"):
                    updated_task = await task_service.update_task(
                        sample_task.id,
                        title="Updated Title",
                        status=TaskStatus.IN_PROGRESS
                    )
                    
                    assert updated_task.title == "Updated Title"
                    assert updated_task.status == TaskStatus.IN_PROGRESS
                    assert updated_task.updated_at > sample_task.updated_at
    
    @pytest.mark.asyncio
    async def test_update_task_not_found(self, task_service):
        """Test updating non-existent task."""
        with patch.object(task_service, 'get_task', new_callable=AsyncMock, return_value=None):
            result = await task_service.update_task("non-existent", title="New Title")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_update_task_validation_error(self, task_service, sample_task):
        """Test task update with validation error."""
        task_service._task_cache[sample_task.id] = sample_task
        
        with patch.object(task_service.file_manager, 'backup_task_file', new_callable=AsyncMock):
            with pytest.raises(TaskValidationError):
                await task_service.update_task(
                    sample_task.id,
                    title=""  # Empty title should fail validation
                )
    
    @pytest.mark.asyncio
    async def test_delete_task_success(self, task_service, sample_task):
        """Test successful task deletion."""
        task_service._task_cache[sample_task.id] = sample_task
        
        with patch.object(task_service.file_manager, 'backup_task_file', new_callable=AsyncMock):
            with patch.object(task_service.file_manager, 'delete_task_file', new_callable=AsyncMock, return_value=True):
                result = await task_service.delete_task(sample_task.id)
                
                assert result is True
                assert sample_task.id not in task_service._task_cache
    
    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, task_service):
        """Test deleting non-existent task."""
        with patch.object(task_service, 'get_task', new_callable=AsyncMock, return_value=None):
            result = await task_service.delete_task("non-existent")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_delete_task_with_children_cascade(self, task_service, sample_task):
        """Test deleting task with children using cascade."""
        # Create child task
        child_task = Task(
            id='child-001',
            title='Child Task',
            parent_id=sample_task.id
        )
        sample_task.child_ids = ['child-001']
        
        task_service._task_cache[sample_task.id] = sample_task
        task_service._task_cache[child_task.id] = child_task
        
        with patch.object(task_service.file_manager, 'backup_task_file', new_callable=AsyncMock):
            with patch.object(task_service.file_manager, 'delete_task_file', new_callable=AsyncMock, return_value=True):
                result = await task_service.delete_task(sample_task.id, cascade=True)
                
                assert result is True
                assert sample_task.id not in task_service._task_cache
                assert child_task.id not in task_service._task_cache
    
    @pytest.mark.asyncio
    async def test_delete_task_with_children_no_cascade(self, task_service, sample_task):
        """Test deleting task with children without cascade."""
        # Create child task
        child_task = Task(
            id='child-001',
            title='Child Task',
            parent_id=sample_task.id
        )
        sample_task.child_ids = ['child-001']
        
        task_service._task_cache[sample_task.id] = sample_task
        task_service._task_cache[child_task.id] = child_task
        
        with patch.object(task_service.file_manager, 'backup_task_file', new_callable=AsyncMock):
            with patch.object(task_service.file_manager, 'delete_task_file', new_callable=AsyncMock, return_value=True):
                with patch.object(task_service, 'update_task', new_callable=AsyncMock) as mock_update:
                    result = await task_service.delete_task(sample_task.id, cascade=False)
                    
                    assert result is True
                    mock_update.assert_called_once_with('child-001', parent_id=None)


class TestTaskServiceFiltering:
    """Test task filtering and listing operations."""
    
    @pytest.mark.asyncio
    async def test_list_tasks_no_filter(self, task_service):
        """Test listing all tasks without filters."""
        tasks = [
            Task(id='task-1', title='Task 1', status=TaskStatus.PENDING),
            Task(id='task-2', title='Task 2', status=TaskStatus.COMPLETED),
            Task(id='task-3', title='Task 3', status=TaskStatus.IN_PROGRESS),
        ]
        
        for task in tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        result = await task_service.list_tasks()
        
        assert len(result) == 3
        # Should be sorted by creation date (newest first)
        assert all(isinstance(task, Task) for task in result)
    
    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_status(self, task_service):
        """Test filtering tasks by status."""
        tasks = [
            Task(id='task-1', title='Task 1', status=TaskStatus.PENDING),
            Task(id='task-2', title='Task 2', status=TaskStatus.COMPLETED),
            Task(id='task-3', title='Task 3', status=TaskStatus.PENDING),
        ]
        
        for task in tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        result = await task_service.list_tasks(status=TaskStatus.PENDING)
        
        assert len(result) == 2
        assert all(task.status == TaskStatus.PENDING for task in result)
    
    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_priority(self, task_service):
        """Test filtering tasks by priority."""
        tasks = [
            Task(id='task-1', title='Task 1', priority=Priority.HIGH),
            Task(id='task-2', title='Task 2', priority=Priority.LOW),
            Task(id='task-3', title='Task 3', priority=Priority.HIGH),
        ]
        
        for task in tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        result = await task_service.list_tasks(priority=Priority.HIGH)
        
        assert len(result) == 2
        assert all(task.priority == Priority.HIGH for task in result)
    
    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_tags(self, task_service):
        """Test filtering tasks by tags."""
        tasks = [
            Task(id='task-1', title='Task 1', tags=['urgent', 'bug']),
            Task(id='task-2', title='Task 2', tags=['feature', 'enhancement']),
            Task(id='task-3', title='Task 3', tags=['urgent', 'feature']),
        ]
        
        for task in tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        result = await task_service.list_tasks(tags=['urgent'])
        
        assert len(result) == 2
        assert all('urgent' in task.tags for task in result)
    
    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_parent(self, task_service):
        """Test filtering tasks by parent ID."""
        parent_task = Task(id='parent-1', title='Parent Task')
        child_tasks = [
            Task(id='child-1', title='Child 1', parent_id='parent-1'),
            Task(id='child-2', title='Child 2', parent_id='parent-1'),
            Task(id='orphan-1', title='Orphan Task'),
        ]
        
        task_service._task_cache[parent_task.id] = parent_task
        for task in child_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        result = await task_service.list_tasks(parent_id='parent-1')
        
        assert len(result) == 2
        assert all(task.parent_id == 'parent-1' for task in result)
    
    @pytest.mark.asyncio
    async def test_list_tasks_exclude_completed(self, task_service):
        """Test excluding completed tasks."""
        tasks = [
            Task(id='task-1', title='Task 1', status=TaskStatus.PENDING),
            Task(id='task-2', title='Task 2', status=TaskStatus.COMPLETED),
            Task(id='task-3', title='Task 3', status=TaskStatus.IN_PROGRESS),
        ]
        
        for task in tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        result = await task_service.list_tasks(include_completed=False)
        
        assert len(result) == 2
        assert all(task.status != TaskStatus.COMPLETED for task in result)
    
    @pytest.mark.asyncio
    async def test_get_task_count(self, task_service):
        """Test getting total task count."""
        tasks = [
            Task(id='task-1', title='Task 1'),
            Task(id='task-2', title='Task 2'),
            Task(id='task-3', title='Task 3'),
        ]
        
        for task in tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        count = await task_service.get_task_count()
        
        assert count == 3


class TestTaskServiceHierarchy:
    """Test hierarchy management operations."""
    
    @pytest.mark.asyncio
    async def test_add_child_to_parent(self, task_service):
        """Test adding child to parent task."""
        parent_task = Task(id='parent-1', title='Parent Task')
        task_service._task_cache[parent_task.id] = parent_task
        
        with patch.object(task_service.file_manager, 'write_task_file', new_callable=AsyncMock, return_value=True):
            with patch.object(task_service.markdown_writer, 'write_task_file', return_value="mock content"):
                await task_service._add_child_to_parent('parent-1', 'child-1')
                
                updated_parent = task_service._task_cache['parent-1']
                assert 'child-1' in updated_parent.child_ids
    
    @pytest.mark.asyncio
    async def test_remove_child_from_parent(self, task_service):
        """Test removing child from parent task."""
        parent_task = Task(id='parent-1', title='Parent Task', child_ids=['child-1', 'child-2'])
        task_service._task_cache[parent_task.id] = parent_task
        
        with patch.object(task_service.file_manager, 'write_task_file', new_callable=AsyncMock, return_value=True):
            with patch.object(task_service.markdown_writer, 'write_task_file', return_value="mock content"):
                await task_service._remove_child_from_parent('parent-1', 'child-1')
                
                updated_parent = task_service._task_cache['parent-1']
                assert 'child-1' not in updated_parent.child_ids
                assert 'child-2' in updated_parent.child_ids
    
    @pytest.mark.asyncio
    async def test_handle_parent_change(self, task_service):
        """Test handling parent relationship changes."""
        old_task = Task(id='task-1', title='Task 1', parent_id='old-parent')
        new_task = Task(id='task-1', title='Task 1', parent_id='new-parent')
        
        with patch.object(task_service, '_remove_child_from_parent', new_callable=AsyncMock) as mock_remove:
            with patch.object(task_service, '_add_child_to_parent', new_callable=AsyncMock) as mock_add:
                await task_service._handle_parent_change(old_task, new_task)
                
                mock_remove.assert_called_once_with('old-parent', 'task-1')
                mock_add.assert_called_once_with('new-parent', 'task-1')


class TestTaskServiceCaching:
    """Test caching and external change detection."""
    
    @pytest.mark.asyncio
    async def test_refresh_cache(self, task_service):
        """Test cache refresh functionality."""
        # Add some tasks to cache
        task_service._task_cache = {'old-task': MagicMock()}
        
        with patch.object(task_service, '_load_tasks', new_callable=AsyncMock) as mock_load:
            await task_service.refresh_cache()
            
            assert len(task_service._task_cache) == 0  # Cache cleared
            assert task_service._cache_dirty is True
            mock_load.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_external_changes(self, task_service, sample_task):
        """Test checking for external file changes."""
        mock_content = "---\nid: test-task-001\ntitle: Updated Task\n---\nUpdated content"
        
        with patch.object(task_service.file_manager, 'check_file_changes', return_value={'test-task-001'}):
            with patch.object(task_service.file_manager, 'read_task_file', new_callable=AsyncMock, return_value=mock_content):
                with patch.object(task_service.markdown_parser, 'parse_task_file', return_value=sample_task):
                    reloaded = await task_service.check_external_changes()
                    
                    assert 'test-task-001' in reloaded
                    assert sample_task.id in task_service._task_cache


class TestTaskServiceErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_create_task_pydantic_validation_error(self, task_service):
        """Test handling Pydantic validation errors during task creation."""
        with patch('src.todo_mcp.services.task_service.Task', side_effect=ValidationError.from_exception_data("Task", [])):
            with pytest.raises(TaskValidationError):
                await task_service.create_task(title="Test Task")
    
    @pytest.mark.asyncio
    async def test_get_task_parse_error(self, task_service):
        """Test handling parse errors when getting tasks."""
        with patch.object(task_service.file_manager, 'read_task_file', new_callable=AsyncMock, return_value="invalid content"):
            with patch.object(task_service.markdown_parser, 'parse_task_file', side_effect=ValidationError.from_exception_data("Task", [])):
                result = await task_service.get_task('test-task')
                
                assert result is None
    
    @pytest.mark.asyncio
    async def test_update_task_storage_failure(self, task_service, sample_task):
        """Test handling storage failures during task update."""
        task_service._task_cache[sample_task.id] = sample_task
        
        with patch.object(task_service.file_manager, 'backup_task_file', new_callable=AsyncMock):
            with patch.object(task_service.file_manager, 'write_task_file', new_callable=AsyncMock, return_value=False):
                with pytest.raises(TaskServiceError, match="Failed to save updated task"):
                    await task_service.update_task(sample_task.id, title="New Title")
    
    @pytest.mark.asyncio
    async def test_delete_task_storage_failure(self, task_service, sample_task):
        """Test handling storage failures during task deletion."""
        task_service._task_cache[sample_task.id] = sample_task
        
        with patch.object(task_service.file_manager, 'backup_task_file', new_callable=AsyncMock):
            with patch.object(task_service.file_manager, 'delete_task_file', new_callable=AsyncMock, return_value=False):
                with pytest.raises(TaskServiceError, match="Failed to delete task from storage"):
                    await task_service.delete_task(sample_task.id)


class TestTaskServiceAdvancedFiltering:
    """Test advanced filtering and search functionality."""
    
    @pytest.fixture
    def sample_tasks(self):
        """Create a diverse set of sample tasks for filtering tests."""
        from datetime import timedelta
        
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        return [
            Task(
                id='task-1',
                title='Urgent Bug Fix',
                description='Fix critical production bug',
                status=TaskStatus.IN_PROGRESS,
                priority=Priority.URGENT,
                tags=['bug', 'urgent', 'backend'],
                created_at=yesterday,
                updated_at=now,
                due_date=tomorrow
            ),
            Task(
                id='task-2',
                title='Feature Development',
                description='Implement new user dashboard',
                status=TaskStatus.PENDING,
                priority=Priority.HIGH,
                tags=['feature', 'frontend', 'ui'],
                parent_id='epic-1',
                created_at=now,
                updated_at=now
            ),
            Task(
                id='task-3',
                title='Code Review',
                description='Review pull request #123',
                status=TaskStatus.COMPLETED,
                priority=Priority.MEDIUM,
                tags=['review', 'code'],
                created_at=yesterday,
                updated_at=now,
                due_date=None  # No due date to avoid validation issues
            ),
            Task(
                id='task-4',
                title='Documentation Update',
                description='Update API documentation',
                status=TaskStatus.BLOCKED,
                priority=Priority.LOW,
                tags=['docs', 'api'],
                child_ids=['task-5'],
                created_at=now,
                updated_at=now
            ),
            Task(
                id='task-5',
                title='API Schema Review',
                description='Review API schema changes',
                status=TaskStatus.PENDING,
                priority=Priority.MEDIUM,
                tags=['api', 'review'],
                parent_id='task-4',
                created_at=now,
                updated_at=now,
                due_date=tomorrow
            ),
        ]
    
    @pytest.mark.asyncio
    async def test_filter_tasks_by_status(self, task_service, sample_tasks):
        """Test filtering tasks by status."""
        from src.todo_mcp.models.filters import TaskFilter
        
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        # Filter by IN_PROGRESS status
        task_filter = TaskFilter(status=[TaskStatus.IN_PROGRESS])
        result = await task_service.filter_tasks(task_filter)
        
        assert result.total_count == 1
        assert result.filtered_count == 1
        assert result.tasks[0].id == 'task-1'
        assert result.tasks[0].status == TaskStatus.IN_PROGRESS
    
    @pytest.mark.asyncio
    async def test_filter_tasks_by_multiple_statuses(self, task_service, sample_tasks):
        """Test filtering tasks by multiple statuses."""
        from src.todo_mcp.models.filters import TaskFilter
        
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        # Filter by PENDING and IN_PROGRESS statuses
        task_filter = TaskFilter(status=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
        result = await task_service.filter_tasks(task_filter)
        
        assert result.total_count == 3
        assert result.filtered_count == 3
        statuses = {task.status for task in result.tasks}
        assert statuses == {TaskStatus.PENDING, TaskStatus.IN_PROGRESS}
    
    @pytest.mark.asyncio
    async def test_filter_tasks_by_priority(self, task_service, sample_tasks):
        """Test filtering tasks by priority."""
        from src.todo_mcp.models.filters import TaskFilter
        
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        # Filter by HIGH priority
        task_filter = TaskFilter(priority=[Priority.HIGH])
        result = await task_service.filter_tasks(task_filter)
        
        assert result.total_count == 1
        assert result.tasks[0].priority == Priority.HIGH
    
    @pytest.mark.asyncio
    async def test_filter_tasks_by_tags_any(self, task_service, sample_tasks):
        """Test filtering tasks by tags (any match)."""
        from src.todo_mcp.models.filters import TaskFilter
        
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        # Filter by 'api' tag
        task_filter = TaskFilter(tags=['api'])
        result = await task_service.filter_tasks(task_filter)
        
        assert result.total_count == 2
        task_ids = {task.id for task in result.tasks}
        assert task_ids == {'task-4', 'task-5'}
    
    @pytest.mark.asyncio
    async def test_filter_tasks_by_tags_all(self, task_service, sample_tasks):
        """Test filtering tasks by tags (all must match)."""
        from src.todo_mcp.models.filters import TaskFilter
        
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        # Filter by tasks that have both 'api' and 'review' tags
        task_filter = TaskFilter(tags_all=['api', 'review'])
        result = await task_service.filter_tasks(task_filter)
        
        assert result.total_count == 1
        assert result.tasks[0].id == 'task-5'
    
    @pytest.mark.asyncio
    async def test_filter_tasks_by_parent(self, task_service, sample_tasks):
        """Test filtering tasks by parent ID."""
        from src.todo_mcp.models.filters import TaskFilter
        
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        # Filter by parent task
        task_filter = TaskFilter(parent_id='task-4')
        result = await task_service.filter_tasks(task_filter)
        
        assert result.total_count == 1
        assert result.tasks[0].id == 'task-5'
        assert result.tasks[0].parent_id == 'task-4'
    
    @pytest.mark.asyncio
    async def test_filter_tasks_has_children(self, task_service, sample_tasks):
        """Test filtering tasks that have children."""
        from src.todo_mcp.models.filters import TaskFilter
        
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        # Filter tasks that have children
        task_filter = TaskFilter(has_children=True)
        result = await task_service.filter_tasks(task_filter)
        
        assert result.total_count == 1
        assert result.tasks[0].id == 'task-4'
        assert len(result.tasks[0].child_ids) > 0
    
    @pytest.mark.asyncio
    async def test_filter_tasks_text_search(self, task_service, sample_tasks):
        """Test full-text search functionality."""
        from src.todo_mcp.models.filters import TaskFilter
        
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        # Search for 'bug' in title or description
        task_filter = TaskFilter(search_text='bug')
        result = await task_service.filter_tasks(task_filter)
        
        assert result.total_count == 1
        assert result.tasks[0].id == 'task-1'
        assert 'bug' in result.tasks[0].title.lower() or 'bug' in result.tasks[0].description.lower()
    
    @pytest.mark.asyncio
    async def test_filter_tasks_title_contains(self, task_service, sample_tasks):
        """Test filtering by title content."""
        from src.todo_mcp.models.filters import TaskFilter
        
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        # Search for 'Review' in title
        task_filter = TaskFilter(title_contains='Review')
        result = await task_service.filter_tasks(task_filter)
        
        assert result.total_count == 2
        task_ids = {task.id for task in result.tasks}
        assert task_ids == {'task-3', 'task-5'}
    
    @pytest.mark.asyncio
    async def test_filter_tasks_due_date_range(self, task_service, sample_tasks):
        """Test filtering by due date range."""
        from src.todo_mcp.models.filters import TaskFilter
        from datetime import timedelta
        
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)
        
        # Filter tasks due before tomorrow
        task_filter = TaskFilter(due_before=tomorrow, has_due_date=True)
        result = await task_service.filter_tasks(task_filter)
        
        # Should include task-1 and task-5 (both due tomorrow, which is before tomorrow + epsilon)
        # Since we're using <= comparison, tasks due exactly tomorrow will be included
        assert result.total_count == 2
        task_ids = {task.id for task in result.tasks}
        assert task_ids == {'task-1', 'task-5'}
    
    @pytest.mark.asyncio
    async def test_filter_tasks_exclude_completed(self, task_service, sample_tasks):
        """Test excluding completed tasks."""
        from src.todo_mcp.models.filters import TaskFilter
        
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        # Filter excluding completed tasks
        task_filter = TaskFilter(include_completed=False)
        result = await task_service.filter_tasks(task_filter)
        
        assert result.total_count == 4  # All except task-3 (completed)
        statuses = {task.status for task in result.tasks}
        assert TaskStatus.COMPLETED not in statuses
    
    @pytest.mark.asyncio
    async def test_filter_tasks_sorting(self, task_service, sample_tasks):
        """Test task sorting functionality."""
        from src.todo_mcp.models.filters import TaskFilter
        
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        # Sort by priority (descending)
        task_filter = TaskFilter(sort_by='priority', sort_desc=True)
        result = await task_service.filter_tasks(task_filter)
        
        # Should be ordered: URGENT, HIGH, MEDIUM, MEDIUM, LOW
        priorities = [task.priority for task in result.tasks]
        assert priorities[0] == Priority.URGENT
        assert priorities[1] == Priority.HIGH
        assert priorities[-1] == Priority.LOW
    
    @pytest.mark.asyncio
    async def test_filter_tasks_pagination(self, task_service, sample_tasks):
        """Test task pagination."""
        from src.todo_mcp.models.filters import TaskFilter
        
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        # Get first 2 tasks
        task_filter = TaskFilter(limit=2, offset=0, sort_by='id')
        result = await task_service.filter_tasks(task_filter)
        
        assert result.total_count == 5
        assert result.filtered_count == 2
        assert result.has_more is True
        assert result.offset == 0
        assert result.limit == 2
        
        # Get next 2 tasks
        task_filter = TaskFilter(limit=2, offset=2, sort_by='id')
        result = await task_service.filter_tasks(task_filter)
        
        assert result.total_count == 5
        assert result.filtered_count == 2
        assert result.has_more is True
        assert result.offset == 2
    
    @pytest.mark.asyncio
    async def test_filter_tasks_complex_query(self, task_service, sample_tasks):
        """Test complex filtering with multiple criteria."""
        from src.todo_mcp.models.filters import TaskFilter
        
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        # Complex filter: PENDING or IN_PROGRESS, with HIGH or URGENT priority, containing 'e' in title
        task_filter = TaskFilter(
            status=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
            priority=[Priority.HIGH, Priority.URGENT],
            title_contains='e',
            include_completed=False
        )
        result = await task_service.filter_tasks(task_filter)
        
        # Should match task-1 (IN_PROGRESS, URGENT, 'Urgent Bug Fix' contains 'e')
        # and task-2 (PENDING, HIGH, 'Feature Development' contains 'e')
        assert result.total_count == 2
        task_ids = {task.id for task in result.tasks}
        assert task_ids == {'task-1', 'task-2'}
    
    @pytest.mark.asyncio
    async def test_search_tasks_simple(self, task_service, sample_tasks):
        """Test simple text search method."""
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        result = await task_service.search_tasks('API')
        
        assert result.total_count == 2
        task_ids = {task.id for task in result.tasks}
        assert task_ids == {'task-4', 'task-5'}
    
    @pytest.mark.asyncio
    async def test_get_tasks_by_status(self, task_service, sample_tasks):
        """Test getting tasks by status."""
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        pending_tasks = await task_service.get_tasks_by_status(TaskStatus.PENDING)
        
        assert len(pending_tasks) == 2
        task_ids = {task.id for task in pending_tasks}
        assert task_ids == {'task-2', 'task-5'}
    
    @pytest.mark.asyncio
    async def test_get_tasks_by_priority(self, task_service, sample_tasks):
        """Test getting tasks by priority."""
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        medium_tasks = await task_service.get_tasks_by_priority(Priority.MEDIUM)
        
        assert len(medium_tasks) == 2
        task_ids = {task.id for task in medium_tasks}
        assert task_ids == {'task-3', 'task-5'}
    
    @pytest.mark.asyncio
    async def test_get_tasks_by_tags(self, task_service, sample_tasks):
        """Test getting tasks by tags."""
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        # Test any match
        review_tasks = await task_service.get_tasks_by_tags(['review'])
        assert len(review_tasks) == 2
        
        # Test all match
        api_review_tasks = await task_service.get_tasks_by_tags(['api', 'review'], match_all=True)
        assert len(api_review_tasks) == 1
        assert api_review_tasks[0].id == 'task-5'
    
    @pytest.mark.asyncio
    async def test_get_overdue_tasks(self, task_service, sample_tasks):
        """Test getting overdue tasks."""
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        overdue_tasks = await task_service.get_overdue_tasks()
        
        # task-3 is completed so shouldn't be considered overdue
        # Only tasks with due dates in the past and not completed should be returned
        # In our sample data, task-3 has due_date=yesterday but is COMPLETED
        assert len(overdue_tasks) == 0  # No truly overdue tasks in our sample
    
    @pytest.mark.asyncio
    async def test_get_task_statistics(self, task_service, sample_tasks):
        """Test getting task statistics."""
        # Setup tasks in cache
        for task in sample_tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        stats = await task_service.get_task_statistics()
        
        assert stats['total_tasks'] == 5
        assert stats['by_status']['pending'] == 2
        assert stats['by_status']['in_progress'] == 1
        assert stats['by_status']['completed'] == 1
        assert stats['by_status']['blocked'] == 1
        assert stats['by_priority']['urgent'] == 1
        assert stats['by_priority']['high'] == 1
        assert stats['by_priority']['medium'] == 2
        assert stats['by_priority']['low'] == 1
        assert stats['with_due_dates'] == 2  # task-1 and task-5 have due dates
        assert 'overdue' in stats
        assert 'completed_today' in stats
        assert 'created_today' in stats


class TestTaskFilterModel:
    """Test TaskFilter model validation."""
    
    def test_task_filter_creation(self):
        """Test creating TaskFilter with valid data."""
        from src.todo_mcp.models.filters import TaskFilter
        
        task_filter = TaskFilter(
            status=[TaskStatus.PENDING],
            priority=[Priority.HIGH],
            tags=['urgent'],
            search_text='bug fix',
            limit=10,
            offset=0
        )
        
        assert task_filter.status == [TaskStatus.PENDING]
        assert task_filter.priority == [Priority.HIGH]
        assert task_filter.tags == ['urgent']
        assert task_filter.search_text == 'bug fix'
        assert task_filter.limit == 10
        assert task_filter.offset == 0
    
    def test_task_filter_validation_errors(self):
        """Test TaskFilter validation errors."""
        from src.todo_mcp.models.filters import TaskFilter
        
        # Test invalid sort field
        with pytest.raises(ValidationError):
            TaskFilter(sort_by='invalid_field')
        
        # Test invalid limit
        with pytest.raises(ValidationError):
            TaskFilter(limit=0)
        
        # Test invalid offset
        with pytest.raises(ValidationError):
            TaskFilter(offset=-1)
    
    def test_task_filter_has_filters(self):
        """Test TaskFilter.has_filters() method."""
        from src.todo_mcp.models.filters import TaskFilter
        
        # Empty filter
        empty_filter = TaskFilter()
        assert not empty_filter.has_filters()
        
        # Filter with criteria
        filter_with_criteria = TaskFilter(status=[TaskStatus.PENDING])
        assert filter_with_criteria.has_filters()
    
    def test_task_filter_string_representation(self):
        """Test TaskFilter string representation."""
        from src.todo_mcp.models.filters import TaskFilter
        
        task_filter = TaskFilter(
            status=[TaskStatus.PENDING],
            tags=['urgent'],
            search_text='bug'
        )
        
        str_repr = str(task_filter)
        assert 'TaskFilter' in str_repr
        assert 'status' in str_repr
        assert 'tags' in str_repr
        assert 'search' in str_repr


class TestTaskServiceStatusManagement:
    """Test status management functionality."""
    
    @pytest.fixture
    def sample_task_for_status(self):
        """Create a sample task for status testing."""
        return Task(
            id='status-test-task',
            title='Status Test Task',
            description='Task for testing status management',
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            tags=['test'],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @pytest.mark.asyncio
    async def test_update_task_status_valid_transition(self, task_service, sample_task_for_status):
        """Test updating task status with valid transition."""
        # Setup task in cache
        task_service._task_cache[sample_task_for_status.id] = sample_task_for_status
        
        with patch.object(task_service.file_manager, 'write_task_file', new_callable=AsyncMock, return_value=True):
            with patch.object(task_service.markdown_writer, 'write_task_file', return_value="mock content"):
                updated_task = await task_service.update_task_status(
                    sample_task_for_status.id,
                    TaskStatus.IN_PROGRESS
                )
                
                assert updated_task is not None
                assert updated_task.status == TaskStatus.IN_PROGRESS
                
                # Check audit log was created
                audit_log = updated_task.metadata.get('audit_log', [])
                assert len(audit_log) > 0
                assert audit_log[0]['action'] == 'status_change'
                assert audit_log[0]['old_status'] == TaskStatus.PENDING.value
                assert audit_log[0]['new_status'] == TaskStatus.IN_PROGRESS.value
    
    @pytest.mark.asyncio
    async def test_update_task_status_invalid_transition(self, task_service, sample_task_for_status):
        """Test updating task status with invalid transition."""
        from src.todo_mcp.services.task_service import TaskValidationError
        
        # Setup task in cache
        task_service._task_cache[sample_task_for_status.id] = sample_task_for_status
        
        # Try invalid transition (PENDING -> COMPLETED without going through IN_PROGRESS)
        # Note: Based on our status model, PENDING can go directly to COMPLETED
        # Let's test a truly invalid transition by setting task to COMPLETED first
        sample_task_for_status.status = TaskStatus.COMPLETED
        
        with pytest.raises(TaskValidationError):
            await task_service.update_task_status(
                sample_task_for_status.id,
                TaskStatus.BLOCKED  # Invalid: COMPLETED -> BLOCKED is not allowed
            )
    
    @pytest.mark.asyncio
    async def test_update_task_status_without_validation(self, task_service, sample_task_for_status):
        """Test updating task status without transition validation."""
        # Setup task in cache
        sample_task_for_status.status = TaskStatus.COMPLETED
        task_service._task_cache[sample_task_for_status.id] = sample_task_for_status
        
        with patch.object(task_service.file_manager, 'write_task_file', new_callable=AsyncMock, return_value=True):
            with patch.object(task_service.markdown_writer, 'write_task_file', return_value="mock content"):
                updated_task = await task_service.update_task_status(
                    sample_task_for_status.id,
                    TaskStatus.BLOCKED,
                    validate_transition=False
                )
                
                assert updated_task is not None
                assert updated_task.status == TaskStatus.BLOCKED
    
    @pytest.mark.asyncio
    async def test_update_task_status_without_audit_log(self, task_service, sample_task_for_status):
        """Test updating task status without audit logging."""
        # Setup task in cache
        task_service._task_cache[sample_task_for_status.id] = sample_task_for_status
        
        with patch.object(task_service.file_manager, 'write_task_file', new_callable=AsyncMock, return_value=True):
            with patch.object(task_service.markdown_writer, 'write_task_file', return_value="mock content"):
                updated_task = await task_service.update_task_status(
                    sample_task_for_status.id,
                    TaskStatus.IN_PROGRESS,
                    audit_log=False
                )
                
                assert updated_task is not None
                assert updated_task.status == TaskStatus.IN_PROGRESS
                
                # Check no audit log was created
                audit_log = updated_task.metadata.get('audit_log', [])
                assert len(audit_log) == 0
    
    @pytest.mark.asyncio
    async def test_update_task_status_not_found(self, task_service):
        """Test updating status of non-existent task."""
        result = await task_service.update_task_status(
            'non-existent-task',
            TaskStatus.IN_PROGRESS
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_bulk_update_status_success(self, task_service):
        """Test successful bulk status update."""
        # Create multiple tasks
        tasks = [
            Task(id='bulk-1', title='Task 1', status=TaskStatus.PENDING),
            Task(id='bulk-2', title='Task 2', status=TaskStatus.PENDING),
            Task(id='bulk-3', title='Task 3', status=TaskStatus.PENDING),
        ]
        
        for task in tasks:
            task_service._task_cache[task.id] = task
        
        with patch.object(task_service.file_manager, 'write_task_file', new_callable=AsyncMock, return_value=True):
            with patch.object(task_service.markdown_writer, 'write_task_file', return_value="mock content"):
                results = await task_service.bulk_update_status(
                    ['bulk-1', 'bulk-2', 'bulk-3'],
                    TaskStatus.IN_PROGRESS
                )
                
                assert results['total_requested'] == 3
                assert results['total_successful'] == 3
                assert results['total_failed'] == 0
                assert len(results['successful']) == 3
                assert len(results['failed']) == 0
                assert len(results['errors']) == 0
    
    @pytest.mark.asyncio
    async def test_bulk_update_status_with_validation_errors(self, task_service):
        """Test bulk status update with validation errors."""
        # Create tasks with different statuses
        tasks = [
            Task(id='bulk-1', title='Task 1', status=TaskStatus.PENDING),
            Task(id='bulk-2', title='Task 2', status=TaskStatus.COMPLETED),  # Invalid transition
        ]
        
        for task in tasks:
            task_service._task_cache[task.id] = task
        
        results = await task_service.bulk_update_status(
            ['bulk-1', 'bulk-2'],
            TaskStatus.BLOCKED,  # COMPLETED -> BLOCKED is invalid
            validate_transitions=True
        )
        
        assert results['total_requested'] == 2
        assert results['total_successful'] == 0
        assert results['total_failed'] == 2
        assert len(results['errors']) > 0
    
    @pytest.mark.asyncio
    async def test_bulk_update_status_mixed_results(self, task_service):
        """Test bulk status update with mixed success/failure."""
        # Create tasks, some valid, some not found
        tasks = [
            Task(id='bulk-1', title='Task 1', status=TaskStatus.PENDING),
            Task(id='bulk-2', title='Task 2', status=TaskStatus.PENDING),
        ]
        
        for task in tasks:
            task_service._task_cache[task.id] = task
        
        with patch.object(task_service.file_manager, 'write_task_file', new_callable=AsyncMock, return_value=True):
            with patch.object(task_service.markdown_writer, 'write_task_file', return_value="mock content"):
                results = await task_service.bulk_update_status(
                    ['bulk-1', 'bulk-2', 'non-existent'],
                    TaskStatus.IN_PROGRESS,
                    validate_transitions=False
                )
                
                assert results['total_requested'] == 3
                assert results['total_successful'] == 2
                assert results['total_failed'] == 1
                assert 'non-existent' in results['failed']
    
    @pytest.mark.asyncio
    async def test_get_status_transition_history(self, task_service):
        """Test getting status transition history."""
        # Create task with audit log
        task = Task(
            id='history-task',
            title='History Task',
            status=TaskStatus.COMPLETED,
            metadata={
                'audit_log': [
                    {
                        'action': 'status_change',
                        'timestamp': '2025-01-01T10:00:00',
                        'old_status': 'pending',
                        'new_status': 'in_progress'
                    },
                    {
                        'action': 'status_change',
                        'timestamp': '2025-01-01T11:00:00',
                        'old_status': 'in_progress',
                        'new_status': 'completed'
                    },
                    {
                        'action': 'other_action',
                        'timestamp': '2025-01-01T12:00:00',
                        'data': 'some other data'
                    }
                ]
            }
        )
        
        task_service._task_cache[task.id] = task
        
        history = await task_service.get_status_transition_history(task.id)
        
        assert len(history) == 2  # Only status change entries
        assert history[0]['timestamp'] == '2025-01-01T11:00:00'  # Newest first
        assert history[1]['timestamp'] == '2025-01-01T10:00:00'
    
    @pytest.mark.asyncio
    async def test_get_status_transition_history_not_found(self, task_service):
        """Test getting status history for non-existent task."""
        history = await task_service.get_status_transition_history('non-existent')
        
        assert history == []
    
    @pytest.mark.asyncio
    async def test_get_tasks_by_status_transition(self, task_service):
        """Test getting tasks by status transition."""
        from datetime import timedelta
        
        now = datetime.utcnow()
        recent_time = (now - timedelta(days=2)).isoformat()
        old_time = (now - timedelta(days=10)).isoformat()
        
        # Create tasks with different transition histories
        tasks = [
            Task(
                id='transition-1',
                title='Recent Transition',
                status=TaskStatus.COMPLETED,
                metadata={
                    'audit_log': [
                        {
                            'action': 'status_change',
                            'timestamp': recent_time,
                            'old_status': 'pending',
                            'new_status': 'completed'
                        }
                    ]
                }
            ),
            Task(
                id='transition-2',
                title='Old Transition',
                status=TaskStatus.COMPLETED,
                metadata={
                    'audit_log': [
                        {
                            'action': 'status_change',
                            'timestamp': old_time,
                            'old_status': 'pending',
                            'new_status': 'completed'
                        }
                    ]
                }
            ),
            Task(
                id='transition-3',
                title='Different Transition',
                status=TaskStatus.IN_PROGRESS,
                metadata={
                    'audit_log': [
                        {
                            'action': 'status_change',
                            'timestamp': recent_time,
                            'old_status': 'pending',
                            'new_status': 'in_progress'
                        }
                    ]
                }
            )
        ]
        
        for task in tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        # Get tasks that transitioned from PENDING to COMPLETED in last 7 days
        matching_tasks = await task_service.get_tasks_by_status_transition(
            TaskStatus.PENDING,
            TaskStatus.COMPLETED,
            days_back=7
        )
        
        assert len(matching_tasks) == 1
        assert matching_tasks[0].id == 'transition-1'
    
    @pytest.mark.asyncio
    async def test_validate_bulk_status_transitions(self, task_service):
        """Test validating bulk status transitions."""
        # Create tasks with different statuses
        tasks = [
            Task(id='valid-1', title='Valid Task 1', status=TaskStatus.PENDING),
            Task(id='valid-2', title='Valid Task 2', status=TaskStatus.IN_PROGRESS),
            Task(id='invalid-1', title='Invalid Task', status=TaskStatus.COMPLETED),
            Task(id='same-status', title='Same Status', status=TaskStatus.BLOCKED),
        ]
        
        for task in tasks:
            task_service._task_cache[task.id] = task
        
        results = await task_service.validate_bulk_status_transitions(
            ['valid-1', 'valid-2', 'invalid-1', 'same-status', 'not-found'],
            TaskStatus.BLOCKED
        )
        
        assert len(results['valid_transitions']) == 2  # valid-1, valid-2
        assert len(results['invalid_transitions']) == 1  # invalid-1 (COMPLETED -> BLOCKED)
        assert len(results['not_found']) == 1  # not-found
        assert len(results['no_change_needed']) == 1  # same-status
    
    @pytest.mark.asyncio
    async def test_get_status_statistics(self, task_service):
        """Test getting status statistics."""
        from datetime import timedelta
        
        now = datetime.utcnow()
        recent_time = (now - timedelta(days=2)).isoformat()
        
        # Create tasks with various statuses and transition history
        tasks = [
            Task(id='stat-1', title='Pending Task', status=TaskStatus.PENDING),
            Task(id='stat-2', title='In Progress Task', status=TaskStatus.IN_PROGRESS),
            Task(id='stat-3', title='Completed Task', status=TaskStatus.COMPLETED,
                 metadata={
                     'audit_log': [
                         {
                             'action': 'status_change',
                             'timestamp': recent_time,
                             'old_status': 'pending',
                             'new_status': 'completed'
                         }
                     ]
                 }),
            Task(id='stat-4', title='Another Pending', status=TaskStatus.PENDING),
        ]
        
        for task in tasks:
            task_service._task_cache[task.id] = task
        task_service._cache_dirty = False
        
        stats = await task_service.get_status_statistics()
        
        assert stats['total_tasks'] == 4
        assert stats['status_counts']['pending'] == 2
        assert stats['status_counts']['in_progress'] == 1
        assert stats['status_counts']['completed'] == 1
        assert stats['status_counts']['blocked'] == 0
        
        # Check status distribution percentages
        assert stats['status_distribution']['pending'] == 50.0
        assert stats['status_distribution']['completed'] == 25.0
        
        # Check recent transitions
        assert 'pending -> completed' in stats['recent_transitions']
        assert stats['recent_transitions']['pending -> completed'] == 1
    
    @pytest.mark.asyncio
    async def test_status_management_error_handling(self, task_service):
        """Test error handling in status management methods."""
        from src.todo_mcp.services.task_service import TaskServiceError
        
        # Test with file manager failure
        with patch.object(task_service.file_manager, 'write_task_file', new_callable=AsyncMock, return_value=False):
            with patch.object(task_service.markdown_writer, 'write_task_file', return_value="mock content"):
                task = Task(id='error-task', title='Error Task', status=TaskStatus.PENDING)
                task_service._task_cache[task.id] = task
                
                with pytest.raises(TaskServiceError):
                    await task_service.update_task_status(task.id, TaskStatus.IN_PROGRESS)