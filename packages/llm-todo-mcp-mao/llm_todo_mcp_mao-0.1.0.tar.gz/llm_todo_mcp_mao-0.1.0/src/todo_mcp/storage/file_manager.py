"""
File operations manager for the Todo MCP system.

This module handles all file system operations, including atomic file operations,
file locking, and monitoring for external changes using Python's pathlib and
file locking mechanisms.
"""

import asyncio
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Set
import threading
import sys

# Cross-platform file locking
if sys.platform == "win32":
    import msvcrt
    import errno
else:
    import fcntl
    import errno

from ..config import TodoConfig


class FileLockError(Exception):
    """Exception raised when file locking fails."""
    pass


class FileManager:
    """
    Manager for file system operations and task file handling.
    
    This class provides a centralized interface for all file operations
    related to task storage and management with atomic operations and file locking.
    """
    
    def __init__(self, config: TodoConfig):
        """
        Initialize the file manager.
        
        Args:
            config: Configuration settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.tasks_dir = config.data_directory / "tasks"
        self.templates_dir = config.data_directory / "templates"
        
        # File monitoring
        self._file_watchers: Dict[str, float] = {}  # task_id -> last_modified
        self._lock = threading.RLock()
        self._file_locks: Dict[str, threading.Lock] = {}
    
    async def initialize(self) -> None:
        """Initialize the file manager and ensure directories exist."""
        self.logger.info("Initializing file manager")
        
        # Ensure directories exist
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        if self.config.backup_enabled:
            self.config.backup_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize file monitoring
        await self._initialize_file_monitoring()
    
    async def cleanup(self) -> None:
        """Cleanup file manager resources."""
        self.logger.info("Cleaning up file manager")
        
        # Clear file watchers
        with self._lock:
            self._file_watchers.clear()
            self._file_locks.clear()
    
    def get_task_file_path(self, task_id: str) -> Path:
        """
        Get the file path for a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Path to the task file
        """
        # Sanitize task_id to prevent path traversal
        safe_task_id = "".join(c for c in task_id if c.isalnum() or c in '-_')
        if not safe_task_id:
            raise ValueError(f"Invalid task ID: {task_id}")
        
        return self.tasks_dir / f"{safe_task_id}.md"
    
    def _get_file_lock(self, task_id: str) -> threading.Lock:
        """Get or create a file lock for the given task ID."""
        with self._lock:
            if task_id not in self._file_locks:
                self._file_locks[task_id] = threading.Lock()
            return self._file_locks[task_id]
    
    async def read_task_file(self, task_id: str) -> Optional[str]:
        """
        Read a task file safely with file locking.
        
        Args:
            task_id: Task identifier
            
        Returns:
            File content if exists, None otherwise
        """
        file_path = self.get_task_file_path(task_id)
        
        if not file_path.exists():
            return None
        
        file_lock = self._get_file_lock(task_id)
        
        try:
            with file_lock:
                # Use asyncio to run file I/O in thread pool
                content = await asyncio.get_event_loop().run_in_executor(
                    None, self._read_file_sync, file_path
                )
                
                # Update file monitoring
                self._update_file_watcher(task_id, file_path)
                
                return content
                
        except Exception as e:
            self.logger.error(f"Failed to read task file {task_id}: {e}")
            return None
    
    def _read_file_sync(self, file_path: Path) -> str:
        """Synchronously read file with proper encoding and cross-platform locking."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Try to acquire a shared lock for reading (cross-platform)
                try:
                    self._acquire_file_lock(f, shared=True)
                except FileLockError:
                    raise FileLockError(f"File is locked: {file_path}")
                
                content = f.read()
                
                # Release the lock
                self._release_file_lock(f)
                
                return content
                
        except UnicodeDecodeError as e:
            self.logger.error(f"Encoding error reading {file_path}: {e}")
            raise
    
    async def write_task_file(self, task_id: str, content: str) -> bool:
        """
        Write a task file atomically with file locking.
        
        Args:
            task_id: Task identifier
            content: File content
            
        Returns:
            True if successful, False otherwise
        """
        file_path = self.get_task_file_path(task_id)
        file_lock = self._get_file_lock(task_id)
        
        try:
            with file_lock:
                # Use asyncio to run file I/O in thread pool
                success = await asyncio.get_event_loop().run_in_executor(
                    None, self._write_file_atomic_sync, file_path, content
                )
                
                if success:
                    # Update file monitoring
                    self._update_file_watcher(task_id, file_path)
                    self.logger.debug(f"Successfully wrote task file: {task_id}")
                
                return success
                
        except Exception as e:
            self.logger.error(f"Failed to write task file {task_id}: {e}")
            return False
    
    def _write_file_atomic_sync(self, file_path: Path, content: str) -> bool:
        """Atomically write file using temporary file and rename."""
        try:
            # Create temporary file in the same directory for atomic rename
            temp_dir = file_path.parent
            
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                dir=temp_dir,
                delete=False,
                suffix='.tmp'
            ) as temp_file:
                
                # Try to acquire an exclusive lock (cross-platform)
                try:
                    self._acquire_file_lock(temp_file, shared=False)
                except FileLockError:
                    raise FileLockError(f"Cannot acquire lock for writing: {file_path}")
                
                # Write content to temporary file
                temp_file.write(content)
                temp_file.flush()
                os.fsync(temp_file.fileno())  # Ensure data is written to disk
                
                temp_path = temp_file.name
            
            # Atomically rename temporary file to target file
            if sys.platform == "win32":
                # On Windows, we need to remove the target file first
                if file_path.exists():
                    file_path.unlink()
            
            os.rename(temp_path, file_path)
            return True
            
        except Exception as e:
            # Clean up temporary file if it exists
            try:
                if 'temp_path' in locals():
                    os.unlink(temp_path)
            except:
                pass
            
            self.logger.error(f"Atomic write failed for {file_path}: {e}")
            return False
    
    async def delete_task_file(self, task_id: str) -> bool:
        """
        Delete a task file safely with file locking.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if successful, False otherwise
        """
        file_path = self.get_task_file_path(task_id)
        
        if not file_path.exists():
            return True  # Already deleted
        
        file_lock = self._get_file_lock(task_id)
        
        try:
            with file_lock:
                # Use asyncio to run file I/O in thread pool
                success = await asyncio.get_event_loop().run_in_executor(
                    None, self._delete_file_sync, file_path
                )
                
                if success:
                    # Remove from file monitoring
                    self._remove_file_watcher(task_id)
                    self.logger.debug(f"Successfully deleted task file: {task_id}")
                
                return success
                
        except Exception as e:
            self.logger.error(f"Failed to delete task file {task_id}: {e}")
            return False
    
    def _delete_file_sync(self, file_path: Path) -> bool:
        """Synchronously delete file."""
        try:
            file_path.unlink()
            return True
        except FileNotFoundError:
            return True  # Already deleted
        except Exception as e:
            self.logger.error(f"Failed to delete {file_path}: {e}")
            return False
    
    async def list_task_files(self) -> List[str]:
        """
        List all task files.
        
        Returns:
            List of task IDs
        """
        try:
            # Use asyncio to run directory listing in thread pool
            task_ids = await asyncio.get_event_loop().run_in_executor(
                None, self._list_task_files_sync
            )
            return task_ids
            
        except Exception as e:
            self.logger.error(f"Failed to list task files: {e}")
            return []
    
    def _list_task_files_sync(self) -> List[str]:
        """Synchronously list task files."""
        task_ids = []
        
        try:
            for file_path in self.tasks_dir.glob("*.md"):
                if file_path.is_file():
                    # Extract task ID from filename (remove .md extension)
                    task_id = file_path.stem
                    task_ids.append(task_id)
            
            return sorted(task_ids)
            
        except Exception as e:
            self.logger.error(f"Error listing task files: {e}")
            return []
    
    async def _initialize_file_monitoring(self) -> None:
        """Initialize file monitoring for automatic reload."""
        try:
            task_ids = await self.list_task_files()
            
            for task_id in task_ids:
                file_path = self.get_task_file_path(task_id)
                self._update_file_watcher(task_id, file_path)
                
            self.logger.info(f"Initialized file monitoring for {len(task_ids)} task files")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize file monitoring: {e}")
    
    def _update_file_watcher(self, task_id: str, file_path: Path) -> None:
        """Update file watcher with current modification time."""
        try:
            if file_path.exists():
                mtime = file_path.stat().st_mtime
                with self._lock:
                    self._file_watchers[task_id] = mtime
        except Exception as e:
            self.logger.warning(f"Failed to update file watcher for {task_id}: {e}")
    
    def _remove_file_watcher(self, task_id: str) -> None:
        """Remove file watcher for a task."""
        with self._lock:
            self._file_watchers.pop(task_id, None)
    
    def check_file_changes(self) -> Set[str]:
        """
        Check for external file changes.
        
        Returns:
            Set of task IDs that have been modified externally
        """
        changed_tasks = set()
        
        try:
            with self._lock:
                for task_id, last_mtime in list(self._file_watchers.items()):
                    file_path = self.get_task_file_path(task_id)
                    
                    if file_path.exists():
                        current_mtime = file_path.stat().st_mtime
                        if current_mtime > last_mtime:
                            changed_tasks.add(task_id)
                            self._file_watchers[task_id] = current_mtime
                    else:
                        # File was deleted externally
                        changed_tasks.add(task_id)
                        del self._file_watchers[task_id]
            
        except Exception as e:
            self.logger.error(f"Error checking file changes: {e}")
        
        return changed_tasks
    
    async def backup_task_file(self, task_id: str) -> bool:
        """
        Create a backup of a task file.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if backup was successful, False otherwise
        """
        if not self.config.backup_enabled:
            return True
        
        try:
            source_path = self.get_task_file_path(task_id)
            if not source_path.exists():
                return False
            
            # Create backup filename with timestamp
            timestamp = int(time.time())
            backup_filename = f"{task_id}_{timestamp}.md"
            backup_path = self.config.backup_directory / backup_filename
            
            # Read source and write to backup
            content = await self.read_task_file(task_id)
            if content is None:
                return False
            
            # Write backup atomically
            success = await asyncio.get_event_loop().run_in_executor(
                None, self._write_file_atomic_sync, backup_path, content
            )
            
            if success:
                self.logger.debug(f"Created backup for task {task_id}: {backup_filename}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to backup task file {task_id}: {e}")
            return False
    
    def _acquire_file_lock(self, file_obj, shared: bool = False) -> None:
        """
        Acquire file lock in a cross-platform way.
        
        Args:
            file_obj: File object to lock
            shared: If True, acquire shared lock; if False, acquire exclusive lock
            
        Raises:
            FileLockError: If lock cannot be acquired
        """
        try:
            if sys.platform == "win32":
                # Windows file locking using msvcrt
                mode = msvcrt.LK_NBLCK if not shared else msvcrt.LK_NBLCK
                msvcrt.locking(file_obj.fileno(), mode, 1)
            else:
                # Unix/Linux file locking using fcntl
                lock_type = fcntl.LOCK_SH if shared else fcntl.LOCK_EX
                fcntl.flock(file_obj.fileno(), lock_type | fcntl.LOCK_NB)
                
        except (OSError, IOError) as e:
            if sys.platform == "win32":
                # Windows locking errors
                raise FileLockError(f"Cannot acquire file lock: {e}")
            else:
                # Unix locking errors
                if e.errno == errno.EAGAIN or e.errno == errno.EACCES:
                    raise FileLockError(f"File is locked")
                raise
    
    def _release_file_lock(self, file_obj) -> None:
        """
        Release file lock in a cross-platform way.
        
        Args:
            file_obj: File object to unlock
        """
        try:
            if sys.platform == "win32":
                # Windows file unlocking
                msvcrt.locking(file_obj.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                # Unix/Linux file unlocking
                fcntl.flock(file_obj.fileno(), fcntl.LOCK_UN)
                
        except (OSError, IOError) as e:
            self.logger.warning(f"Failed to release file lock: {e}")