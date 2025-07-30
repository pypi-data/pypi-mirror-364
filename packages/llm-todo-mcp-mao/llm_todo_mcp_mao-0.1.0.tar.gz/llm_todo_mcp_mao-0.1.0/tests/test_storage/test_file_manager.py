"""
Unit tests for the FileManager class.

Tests atomic file operations, file locking, and monitoring functionality.
"""

import asyncio
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.todo_mcp.storage.file_manager import FileManager, FileLockError
from src.todo_mcp.config import TodoConfig


class TestFileManager:
    """Test cases for FileManager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def config(self, temp_dir):
        """Create a test configuration."""
        config = Mock(spec=TodoConfig)
        config.data_directory = temp_dir
        config.backup_enabled = True
        config.backup_directory = temp_dir / "backups"
        return config
    
    @pytest.fixture
    async def file_manager(self, config):
        """Create and initialize a FileManager instance."""
        manager = FileManager(config)
        await manager.initialize()
        yield manager
        await manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_initialize_creates_directories(self, config, temp_dir):
        """Test that initialization creates required directories."""
        manager = FileManager(config)
        await manager.initialize()
        
        assert (temp_dir / "tasks").exists()
        assert (temp_dir / "templates").exists()
        assert (temp_dir / "backups").exists()
        
        await manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_get_task_file_path(self, file_manager):
        """Test task file path generation."""
        path = file_manager.get_task_file_path("test-task-123")
        
        assert path.name == "test-task-123.md"
        assert path.parent == file_manager.tasks_dir
    
    @pytest.mark.asyncio
    async def test_get_task_file_path_sanitization(self, file_manager):
        """Test task ID sanitization for security."""
        # Test path traversal prevention
        with pytest.raises(ValueError):
            file_manager.get_task_file_path("../../../etc/passwd")
        
        # Test invalid characters
        with pytest.raises(ValueError):
            file_manager.get_task_file_path("")
        
        # Test valid sanitization
        path = file_manager.get_task_file_path("task@#$%^&*()123")
        assert path.name == "task123.md"
    
    @pytest.mark.asyncio
    async def test_write_and_read_task_file(self, file_manager):
        """Test writing and reading task files."""
        task_id = "test-task"
        content = "# Test Task\n\nThis is a test task."
        
        # Write file
        success = await file_manager.write_task_file(task_id, content)
        assert success is True
        
        # Read file
        read_content = await file_manager.read_task_file(task_id)
        assert read_content == content
    
    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self, file_manager):
        """Test reading a file that doesn't exist."""
        content = await file_manager.read_task_file("nonexistent-task")
        assert content is None
    
    @pytest.mark.asyncio
    async def test_write_file_atomic_operation(self, file_manager):
        """Test that file writing is atomic."""
        task_id = "atomic-test"
        content = "Atomic write test content"
        
        # Write file
        success = await file_manager.write_task_file(task_id, content)
        assert success is True
        
        # Verify file exists and has correct content
        file_path = file_manager.get_task_file_path(task_id)
        assert file_path.exists()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            assert f.read() == content
    
    @pytest.mark.asyncio
    async def test_delete_task_file(self, file_manager):
        """Test deleting task files."""
        task_id = "delete-test"
        content = "Content to be deleted"
        
        # Create file
        await file_manager.write_task_file(task_id, content)
        file_path = file_manager.get_task_file_path(task_id)
        assert file_path.exists()
        
        # Delete file
        success = await file_manager.delete_task_file(task_id)
        assert success is True
        assert not file_path.exists()
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_file(self, file_manager):
        """Test deleting a file that doesn't exist."""
        success = await file_manager.delete_task_file("nonexistent-task")
        assert success is True  # Should return True for already deleted files
    
    @pytest.mark.asyncio
    async def test_list_task_files(self, file_manager):
        """Test listing task files."""
        # Create some test files
        task_ids = ["task-1", "task-2", "task-3"]
        
        for task_id in task_ids:
            await file_manager.write_task_file(task_id, f"Content for {task_id}")
        
        # List files
        listed_ids = await file_manager.list_task_files()
        
        assert sorted(listed_ids) == sorted(task_ids)
    
    @pytest.mark.asyncio
    async def test_list_empty_directory(self, file_manager):
        """Test listing files in empty directory."""
        task_ids = await file_manager.list_task_files()
        assert task_ids == []
    
    @pytest.mark.asyncio
    async def test_file_monitoring_update(self, file_manager):
        """Test file monitoring functionality."""
        task_id = "monitor-test"
        file_path = file_manager.get_task_file_path(task_id)
        
        # Create a file
        file_path.write_text("Test content", encoding='utf-8')
        
        # Update file watcher
        file_manager._update_file_watcher(task_id, file_path)
        
        # Check that file is being monitored
        assert task_id in file_manager._file_watchers
        assert file_manager._file_watchers[task_id] > 0
    
    @pytest.mark.asyncio
    async def test_check_file_changes(self, file_manager):
        """Test checking for external file changes."""
        task_id = "change-test"
        file_path = file_manager.get_task_file_path(task_id)
        
        # Create and monitor file
        file_path.write_text("Original content", encoding='utf-8')
        file_manager._update_file_watcher(task_id, file_path)
        
        # Simulate external change by updating modification time
        import time
        time.sleep(0.1)  # Ensure different timestamp
        file_path.write_text("Modified content", encoding='utf-8')
        
        # Check for changes
        changed_tasks = file_manager.check_file_changes()
        assert task_id in changed_tasks
    
    @pytest.mark.asyncio
    async def test_backup_task_file(self, file_manager):
        """Test creating backup files."""
        task_id = "backup-test"
        content = "Content to backup"
        
        # Create original file
        await file_manager.write_task_file(task_id, content)
        
        # Create backup
        success = await file_manager.backup_task_file(task_id)
        assert success is True
        
        # Check backup exists
        backup_files = list(file_manager.config.backup_directory.glob(f"{task_id}_*.md"))
        assert len(backup_files) == 1
        
        # Verify backup content
        backup_content = backup_files[0].read_text(encoding='utf-8')
        assert backup_content == content
    
    @pytest.mark.asyncio
    async def test_backup_nonexistent_file(self, file_manager):
        """Test backing up a file that doesn't exist."""
        success = await file_manager.backup_task_file("nonexistent-task")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_backup_disabled(self, config, temp_dir):
        """Test behavior when backup is disabled."""
        config.backup_enabled = False
        manager = FileManager(config)
        await manager.initialize()
        
        success = await manager.backup_task_file("any-task")
        assert success is True  # Should return True when backup is disabled
        
        await manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_concurrent_file_operations(self, file_manager):
        """Test concurrent file operations with locking."""
        task_id = "concurrent-test"
        
        async def write_operation(content_suffix):
            content = f"Concurrent content {content_suffix}"
            return await file_manager.write_task_file(task_id, content)
        
        # Run multiple concurrent write operations
        tasks = [write_operation(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All operations should succeed
        assert all(results)
        
        # File should exist and have content from one of the operations
        final_content = await file_manager.read_task_file(task_id)
        assert final_content is not None
        assert "Concurrent content" in final_content
    
    @pytest.mark.asyncio
    async def test_unicode_content_handling(self, file_manager):
        """Test handling of Unicode content."""
        task_id = "unicode-test"
        content = "Unicode test: 你好世界 🌍 émojis and spëcial chars"
        
        # Write and read Unicode content
        success = await file_manager.write_task_file(task_id, content)
        assert success is True
        
        read_content = await file_manager.read_task_file(task_id)
        assert read_content == content
    
    @pytest.mark.asyncio
    async def test_large_file_handling(self, file_manager):
        """Test handling of large files."""
        task_id = "large-file-test"
        # Create content that's about 1MB
        content = "Large file content line.\n" * 50000
        
        # Write and read large content
        success = await file_manager.write_task_file(task_id, content)
        assert success is True
        
        read_content = await file_manager.read_task_file(task_id)
        assert read_content == content
        assert len(read_content) > 1000000  # Verify it's actually large
    
    @pytest.mark.asyncio
    async def test_file_lock_acquisition(self, file_manager):
        """Test file lock acquisition and release."""
        task_id = "lock-test"
        lock = file_manager._get_file_lock(task_id)
        
        # Should be able to acquire lock
        assert lock.acquire(blocking=False) is True
        
        # Should be able to release lock
        lock.release()
        
        # Should be able to acquire again
        assert lock.acquire(blocking=False) is True
        lock.release()
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_path(self, file_manager):
        """Test error handling with invalid file paths."""
        # Test with invalid task ID that creates invalid path
        with patch.object(file_manager, 'get_task_file_path') as mock_path:
            mock_path.side_effect = OSError("Invalid path")
            
            success = await file_manager.write_task_file("invalid", "content")
            assert success is False
    
    @pytest.mark.asyncio
    async def test_cleanup_removes_watchers(self, file_manager):
        """Test that cleanup removes file watchers."""
        task_id = "cleanup-test"
        file_path = file_manager.get_task_file_path(task_id)
        
        # Create file and add to watchers
        file_path.write_text("Test content", encoding='utf-8')
        file_manager._update_file_watcher(task_id, file_path)
        
        assert task_id in file_manager._file_watchers
        
        # Cleanup should remove watchers
        await file_manager.cleanup()
        
        assert len(file_manager._file_watchers) == 0