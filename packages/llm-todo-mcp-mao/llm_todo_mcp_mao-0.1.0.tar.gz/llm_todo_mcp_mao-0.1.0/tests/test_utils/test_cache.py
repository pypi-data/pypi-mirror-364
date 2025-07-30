"""
Tests for the caching utilities.

This module tests the LRU cache implementation, task-specific caching,
and cache management functionality.
"""

import json
import pickle
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from todo_mcp.models.task import Task, TaskStatus, Priority
from todo_mcp.utils.cache import (
    CacheEntry,
    LRUCache,
    TaskCache,
    CacheManager,
    get_cache_manager,
    initialize_cache,
)


class TestCacheEntry:
    """Test the CacheEntry class."""
    
    def test_cache_entry_creation(self):
        """Test basic cache entry creation."""
        value = "test_value"
        entry = CacheEntry(value)
        
        assert entry.value == value
        assert entry.access_count == 1
        assert entry.ttl is None
        assert not entry.is_expired()
    
    def test_cache_entry_with_ttl(self):
        """Test cache entry with TTL."""
        value = "test_value"
        ttl = 0.1  # 100ms
        entry = CacheEntry(value, ttl)
        
        assert not entry.is_expired()
        time.sleep(0.15)
        assert entry.is_expired()
    
    def test_cache_entry_touch(self):
        """Test cache entry access tracking."""
        entry = CacheEntry("test")
        initial_access_time = entry.last_accessed
        initial_count = entry.access_count
        
        time.sleep(0.01)
        entry.touch()
        
        assert entry.last_accessed > initial_access_time
        assert entry.access_count == initial_count + 1


class TestLRUCache:
    """Test the LRU cache implementation."""
    
    def test_basic_operations(self):
        """Test basic cache operations."""
        cache = LRUCache[str](max_size=3)
        
        # Test put and get
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.get("nonexistent") is None
        
        # Test size
        assert cache.size() == 1
        
        # Test keys
        assert cache.keys() == {"key1"}
    
    def test_lru_eviction(self):
        """Test LRU eviction policy."""
        cache = LRUCache[str](max_size=2)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.size() == 2
    
    def test_lru_access_order(self):
        """Test that accessing items affects eviction order."""
        cache = LRUCache[str](max_size=2)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        # Access key1 to make it recently used
        cache.get("key1")
        
        # Add key3, should evict key2 (least recently used)
        cache.put("key3", "value3")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"
    
    def test_ttl_expiration(self):
        """Test TTL-based expiration."""
        cache = LRUCache[str](max_size=10, default_ttl=0.1)
        
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        time.sleep(0.15)
        assert cache.get("key1") is None
        assert cache.size() == 0
    
    def test_update_existing_key(self):
        """Test updating an existing key."""
        cache = LRUCache[str](max_size=10)
        
        cache.put("key1", "value1")
        cache.put("key1", "value2")
        
        assert cache.get("key1") == "value2"
        assert cache.size() == 1
    
    def test_delete_operation(self):
        """Test cache deletion."""
        cache = LRUCache[str](max_size=10)
        
        cache.put("key1", "value1")
        assert cache.delete("key1") is True
        assert cache.get("key1") is None
        assert cache.delete("nonexistent") is False
    
    def test_clear_operation(self):
        """Test cache clearing."""
        cache = LRUCache[str](max_size=10)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.clear()
        
        assert cache.size() == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_cleanup_expired(self):
        """Test cleanup of expired entries."""
        cache = LRUCache[str](max_size=10)
        
        cache.put("key1", "value1", ttl=0.1)
        cache.put("key2", "value2", ttl=1.0)
        cache.put("key3", "value3")  # No TTL
        
        time.sleep(0.15)
        expired_count = cache.cleanup_expired()
        
        assert expired_count == 1
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_cache_statistics(self):
        """Test cache statistics tracking."""
        cache = LRUCache[str](max_size=2)
        
        # Test hits and misses
        cache.put("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("nonexistent")  # Miss
        
        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5
        assert stats['size'] == 1
        assert stats['max_size'] == 2
        
        # Test evictions
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # Should cause eviction
        
        stats = cache.get_stats()
        assert stats['evictions'] == 1
    
    def test_thread_safety(self):
        """Test thread safety of cache operations."""
        cache = LRUCache[int](max_size=100)
        results = []
        
        def worker(start_num: int):
            for i in range(start_num, start_num + 10):
                cache.put(f"key{i}", i)
                value = cache.get(f"key{i}")
                results.append(value)
        
        threads = []
        for i in range(0, 50, 10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All operations should have succeeded
        assert len(results) == 50
        assert all(result is not None for result in results)


class TestTaskCache:
    """Test the TaskCache implementation."""
    
    def create_test_task(self, task_id: str, parent_id: str = None, child_ids: list = None) -> Task:
        """Create a test task."""
        return Task(
            id=task_id,
            title=f"Test Task {task_id}",
            description="Test description",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            tags=["test"],
            parent_id=parent_id,
            child_ids=child_ids or [],
            tool_calls=[],
            metadata={}
        )
    
    def test_task_operations(self):
        """Test basic task cache operations."""
        cache = TaskCache(max_size=10)
        task = self.create_test_task("task1")
        
        cache.put_task(task)
        retrieved_task = cache.get_task("task1")
        
        assert retrieved_task is not None
        assert retrieved_task.id == "task1"
        assert retrieved_task.title == "Test Task task1"
    
    def test_task_deletion_with_dependencies(self):
        """Test task deletion and dependency invalidation."""
        cache = TaskCache(max_size=10)
        
        parent_task = self.create_test_task("parent", child_ids=["child1", "child2"])
        child_task = self.create_test_task("child1", parent_id="parent")
        
        cache.put_task(parent_task)
        cache.put_task(child_task)
        
        # Cache some hierarchy data
        cache.put_hierarchy("parent", {"children": ["child1", "child2"]})
        
        # Delete parent task
        cache.delete_task("parent")
        
        assert cache.get_task("parent") is None
        assert cache.get_hierarchy("parent") is None  # Should be invalidated
    
    def test_hierarchy_caching(self):
        """Test hierarchy data caching."""
        cache = TaskCache(max_size=10)
        
        hierarchy_data = {
            "root": "task1",
            "children": ["task2", "task3"],
            "depth": 2
        }
        
        cache.put_hierarchy("task1", hierarchy_data)
        retrieved_data = cache.get_hierarchy("task1")
        
        assert retrieved_data == hierarchy_data
    
    def test_query_result_caching(self):
        """Test query result caching."""
        cache = TaskCache(max_size=10)
        
        query_result = {
            "tasks": ["task1", "task2"],
            "total": 2,
            "filters": {"status": "pending"}
        }
        
        cache.put_query_result("pending_tasks", query_result)
        retrieved_result = cache.get_query_result("pending_tasks")
        
        assert retrieved_result == query_result
    
    def test_query_invalidation(self):
        """Test query cache invalidation."""
        cache = TaskCache(max_size=10)
        
        cache.put_query_result("query1", {"result": "data1"})
        cache.put_query_result("query2", {"result": "data2"})
        
        cache.invalidate_queries()
        
        assert cache.get_query_result("query1") is None
        assert cache.get_query_result("query2") is None
    
    def test_bulk_operations(self):
        """Test bulk task operations."""
        cache = TaskCache(max_size=10)
        
        tasks = {
            "task1": self.create_test_task("task1"),
            "task2": self.create_test_task("task2"),
            "task3": self.create_test_task("task3")
        }
        
        cache.bulk_put_tasks(tasks)
        
        for task_id in tasks:
            assert cache.get_task(task_id) is not None
    
    def test_cache_statistics(self):
        """Test comprehensive cache statistics."""
        cache = TaskCache(max_size=10)
        
        task = self.create_test_task("task1")
        cache.put_task(task)
        cache.put_hierarchy("task1", {"data": "test"})
        cache.put_query_result("query1", {"result": "test"})
        
        stats = cache.get_stats()
        
        assert 'task_cache' in stats
        assert 'hierarchy_cache' in stats
        assert 'query_cache' in stats
        assert 'dependencies_tracked' in stats
        assert stats['dependencies_tracked'] >= 0


class TestCacheManager:
    """Test the CacheManager implementation."""
    
    def test_cache_manager_initialization(self):
        """Test cache manager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            manager = CacheManager(config_dir)
            
            assert manager.config_dir == config_dir
            assert isinstance(manager.task_cache, TaskCache)
    
    def test_persistence_operations(self):
        """Test cache persistence to disk."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            manager = CacheManager(config_dir)
            
            # Add some test data
            task = Task(
                id="test_task",
                title="Test Task",
                description="Test description",
                status=TaskStatus.PENDING,
                priority=Priority.MEDIUM,
                tags=["test"],
                parent_id=None,
                child_ids=[],
                tool_calls=[],
                metadata={}
            )
            
            manager.task_cache.put_task(task)
            
            # Save to disk
            manager.save_to_disk()
            
            # Create new manager and load
            new_manager = CacheManager(config_dir)
            loaded_count = new_manager.load_from_disk()
            
            assert loaded_count == 1
            loaded_task = new_manager.task_cache.get_task("test_task")
            assert loaded_task is not None
            assert loaded_task.title == "Test Task"
    
    def test_persistence_disabled(self):
        """Test cache manager with persistence disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            manager = CacheManager(config_dir)
            manager.enable_persistence(False)
            
            # These operations should not create files
            manager.save_to_disk()
            loaded_count = manager.load_from_disk()
            
            assert loaded_count == 0
            assert not (config_dir / "task_cache.pkl").exists()
    
    def test_prewarm_cache(self):
        """Test cache prewarming."""
        manager = CacheManager()
        
        def mock_task_loader():
            return {
                "task1": Task(
                    id="task1",
                    title="Task 1",
                    description="Description 1",
                    status=TaskStatus.PENDING,
                    priority=Priority.HIGH,
                    tags=[],
                    parent_id=None,
                    child_ids=[],
                    tool_calls=[],
                    metadata={}
                ),
                "task2": Task(
                    id="task2",
                    title="Task 2",
                    description="Description 2",
                    status=TaskStatus.IN_PROGRESS,
                    priority=Priority.LOW,
                    tags=[],
                    parent_id=None,
                    child_ids=[],
                    tool_calls=[],
                    metadata={}
                )
            }
        
        prewarmed_count = manager.prewarm_cache(mock_task_loader)
        
        assert prewarmed_count == 2
        assert manager.task_cache.get_task("task1") is not None
        assert manager.task_cache.get_task("task2") is not None
    
    def test_periodic_cleanup(self):
        """Test periodic cleanup functionality."""
        manager = CacheManager()
        manager._cleanup_interval = 0.1  # Very short interval for testing
        
        initial_cleanup_time = manager._last_cleanup
        time.sleep(0.15)
        
        manager.periodic_cleanup()
        
        assert manager._last_cleanup > initial_cleanup_time
    
    def test_global_statistics(self):
        """Test global cache statistics."""
        manager = CacheManager()
        
        stats = manager.get_global_stats()
        
        assert 'task_cache' in stats
        assert 'hierarchy_cache' in stats
        assert 'query_cache' in stats
        assert 'persistence_enabled' in stats
        assert 'last_cleanup' in stats
    
    def test_clear_all_caches(self):
        """Test clearing all caches."""
        manager = CacheManager()
        
        # Add some test data
        task = Task(
            id="test_task",
            title="Test Task",
            description="Test description",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            tags=[],
            parent_id=None,
            child_ids=[],
            tool_calls=[],
            metadata={}
        )
        
        manager.task_cache.put_task(task)
        manager.task_cache.put_hierarchy("test", {"data": "test"})
        manager.task_cache.put_query_result("test_query", {"result": "test"})
        
        manager.clear_all_caches()
        
        assert manager.task_cache.get_task("test_task") is None
        assert manager.task_cache.get_hierarchy("test") is None
        assert manager.task_cache.get_query_result("test_query") is None


class TestGlobalCacheManager:
    """Test global cache manager functions."""
    
    def test_get_cache_manager_singleton(self):
        """Test that get_cache_manager returns the same instance."""
        manager1 = get_cache_manager()
        manager2 = get_cache_manager()
        
        assert manager1 is manager2
    
    def test_initialize_cache(self):
        """Test cache initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            manager = initialize_cache(config_dir)
            
            assert isinstance(manager, CacheManager)
            assert manager.config_dir == config_dir
            
            # Should return the same instance
            same_manager = get_cache_manager()
            assert same_manager is manager


class TestCacheIntegration:
    """Integration tests for cache functionality."""
    
    def test_cache_with_real_task_operations(self):
        """Test cache integration with realistic task operations."""
        cache = TaskCache(max_size=100)
        
        # Create a hierarchy of tasks
        parent = Task(
            id="epic_001",
            title="User Authentication Epic",
            description="Complete user authentication system",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.HIGH,
            tags=["epic", "auth"],
            parent_id=None,
            child_ids=["task_001", "task_002"],
            tool_calls=[],
            metadata={"estimated_hours": 40}
        )
        
        child1 = Task(
            id="task_001",
            title="Implement login endpoint",
            description="Create secure login endpoint",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            tags=["backend", "auth"],
            parent_id="epic_001",
            child_ids=[],
            tool_calls=[],
            metadata={"estimated_hours": 8}
        )
        
        child2 = Task(
            id="task_002",
            title="Create user registration",
            description="Implement user registration flow",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            tags=["backend", "auth"],
            parent_id="epic_001",
            child_ids=[],
            tool_calls=[],
            metadata={"estimated_hours": 12}
        )
        
        # Cache the tasks
        cache.put_task(parent)
        cache.put_task(child1)
        cache.put_task(child2)
        
        # Cache hierarchy data
        hierarchy_data = {
            "root": parent.id,
            "children": [child1.id, child2.id],
            "total_estimated_hours": 20
        }
        cache.put_hierarchy(parent.id, hierarchy_data)
        
        # Cache query results
        pending_tasks_query = {
            "tasks": [child1.id, child2.id],
            "count": 2,
            "filter": {"status": "pending"}
        }
        cache.put_query_result("pending_tasks", pending_tasks_query)
        
        # Verify all data is cached correctly
        assert cache.get_task(parent.id).title == "User Authentication Epic"
        assert cache.get_task(child1.id).parent_id == parent.id
        assert cache.get_hierarchy(parent.id)["total_estimated_hours"] == 20
        assert cache.get_query_result("pending_tasks")["count"] == 2
        
        # Test dependency invalidation
        cache.delete_task(parent.id)
        
        # Parent should be gone, hierarchy invalidated, queries cleared
        assert cache.get_task(parent.id) is None
        assert cache.get_hierarchy(parent.id) is None
        # Child tasks should still exist
        assert cache.get_task(child1.id) is not None
        assert cache.get_task(child2.id) is not None
    
    def test_performance_characteristics(self):
        """Test cache performance characteristics."""
        cache = TaskCache(max_size=1000)
        
        # Measure bulk insertion time
        start_time = time.time()
        
        tasks = {}
        for i in range(500):
            task = Task(
                id=f"task_{i:03d}",
                title=f"Task {i}",
                description=f"Description for task {i}",
                status=TaskStatus.PENDING,
                priority=Priority.MEDIUM,
                tags=[f"tag_{i % 10}"],
                parent_id=None,
                child_ids=[],
                tool_calls=[],
                metadata={"index": i}
            )
            tasks[task.id] = task
        
        cache.bulk_put_tasks(tasks)
        bulk_insert_time = time.time() - start_time
        
        # Measure retrieval time
        start_time = time.time()
        for i in range(500):
            task = cache.get_task(f"task_{i:03d}")
            assert task is not None
        
        retrieval_time = time.time() - start_time
        
        # Performance should be reasonable
        assert bulk_insert_time < 1.0  # Should insert 500 tasks in under 1 second
        assert retrieval_time < 0.5    # Should retrieve 500 tasks in under 0.5 seconds
        
        # Cache should have good hit rate
        stats = cache.get_stats()
        assert stats['task_cache']['hit_rate'] > 0.9  # Should have >90% hit rate