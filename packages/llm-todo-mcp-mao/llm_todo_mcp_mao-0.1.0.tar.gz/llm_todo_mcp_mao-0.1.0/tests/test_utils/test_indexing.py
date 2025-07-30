"""
Tests for the indexing and query optimization utilities.

This module tests the various index implementations, query optimization,
and performance characteristics of the indexing system.
"""

import time
from datetime import datetime, timedelta
from typing import List

import pytest

from todo_mcp.models.task import Task, TaskStatus, Priority
from todo_mcp.models.filters import TaskFilter
from todo_mcp.utils.indexing import (
    IndexEntry,
    BaseIndex,
    HashIndex,
    RangeIndex,
    TextIndex,
    TaskIndexManager,
    QueryOptimizer,
    QueryResult,
    PaginatedResult,
    get_index_manager,
    initialize_indexing,
)


class TestIndexEntry:
    """Test the IndexEntry class."""
    
    def test_index_entry_creation(self):
        """Test basic index entry creation."""
        entry = IndexEntry("task_001", "test_value")
        
        assert entry.task_id == "task_001"
        assert entry.value == "test_value"
        assert isinstance(entry.timestamp, datetime)


class TestBaseIndex:
    """Test the BaseIndex class."""
    
    def test_basic_operations(self):
        """Test basic index operations."""
        index = BaseIndex()
        
        index.add("task_001", "value1")
        assert index.size() == 1
        
        index.add("task_002", "value2")
        assert index.size() == 2
        
        index.remove("task_001")
        assert index.size() == 1
        
        index.clear()
        assert index.size() == 0


class TestHashIndex:
    """Test the HashIndex implementation."""
    
    def test_exact_lookups(self):
        """Test exact value lookups."""
        index = HashIndex()
        
        index.add("task_001", "pending")
        index.add("task_002", "completed")
        index.add("task_003", "pending")
        
        pending_tasks = index.find_exact("pending")
        assert pending_tasks == {"task_001", "task_003"}
        
        completed_tasks = index.find_exact("completed")
        assert completed_tasks == {"task_002"}
        
        nonexistent = index.find_exact("nonexistent")
        assert nonexistent == set()
    
    def test_multiple_value_lookup(self):
        """Test finding tasks matching any of multiple values."""
        index = HashIndex()
        
        index.add("task_001", "high")
        index.add("task_002", "medium")
        index.add("task_003", "low")
        index.add("task_004", "high")
        
        high_medium_tasks = index.find_any(["high", "medium"])
        assert high_medium_tasks == {"task_001", "task_002", "task_004"}
    
    def test_value_updates(self):
        """Test updating values in the index."""
        index = HashIndex()
        
        index.add("task_001", "pending")
        assert index.find_exact("pending") == {"task_001"}
        
        # Update the same task with new value
        index.add("task_001", "completed")
        assert index.find_exact("pending") == set()
        assert index.find_exact("completed") == {"task_001"}
    
    def test_get_all_values(self):
        """Test getting all unique values."""
        index = HashIndex()
        
        index.add("task_001", "pending")
        index.add("task_002", "completed")
        index.add("task_003", "pending")
        
        all_values = index.get_all_values()
        assert all_values == {"pending", "completed"}


class TestRangeIndex:
    """Test the RangeIndex implementation."""
    
    def test_range_queries(self):
        """Test range-based queries."""
        index = RangeIndex()
        
        # Add numeric values
        index.add("task_001", 10)
        index.add("task_002", 20)
        index.add("task_003", 30)
        index.add("task_004", 40)
        
        # Test range query
        range_results = index.find_range(15, 35)
        assert range_results == {"task_002", "task_003"}
        
        # Test open-ended ranges
        less_than_25 = index.find_less_than(25)
        assert less_than_25 == {"task_001", "task_002"}
        
        greater_than_25 = index.find_greater_than(25)
        assert greater_than_25 == {"task_003", "task_004"}
    
    def test_date_range_queries(self):
        """Test range queries with datetime objects."""
        index = RangeIndex()
        
        base_date = datetime(2024, 1, 1)
        index.add("task_001", base_date)
        index.add("task_002", base_date + timedelta(days=1))
        index.add("task_003", base_date + timedelta(days=2))
        index.add("task_004", base_date + timedelta(days=3))
        
        # Test date range
        start_date = base_date + timedelta(hours=12)  # Middle of day 1
        end_date = base_date + timedelta(days=2, hours=12)  # Middle of day 3
        
        range_results = index.find_range(start_date, end_date)
        assert range_results == {"task_002", "task_003"}
    
    def test_sorting_maintenance(self):
        """Test that the index maintains sorted order."""
        index = RangeIndex()
        
        # Add values in random order
        index.add("task_003", 30)
        index.add("task_001", 10)
        index.add("task_004", 40)
        index.add("task_002", 20)
        
        # Range query should still work correctly
        range_results = index.find_range(15, 35)
        assert range_results == {"task_002", "task_003"}


class TestTextIndex:
    """Test the TextIndex implementation."""
    
    def test_basic_text_search(self):
        """Test basic text search functionality."""
        index = TextIndex()
        
        index.add("task_001", "Implement user authentication system")
        index.add("task_002", "Create user registration form")
        index.add("task_003", "Design database schema")
        index.add("task_004", "Implement authentication middleware")
        
        # Search for single word
        auth_results = index.search("authentication")
        assert auth_results == {"task_001", "task_004"}
        
        # Search for multiple words (AND operation)
        user_auth_results = index.search("user authentication")
        assert user_auth_results == {"task_001"}
    
    def test_text_search_any(self):
        """Test text search with OR operation."""
        index = TextIndex()
        
        index.add("task_001", "Implement user authentication")
        index.add("task_002", "Create user registration")
        index.add("task_003", "Design database schema")
        
        # Search for any of the words
        user_or_database = index.search_any("user database")
        assert user_or_database == {"task_001", "task_002", "task_003"}
    
    def test_prefix_search(self):
        """Test prefix-based search."""
        index = TextIndex()
        
        index.add("task_001", "Authentication system")
        index.add("task_002", "Authorization middleware")
        index.add("task_003", "Database connection")
        
        # Search with prefix
        auth_prefix_results = index.search_prefix("auth")
        assert auth_prefix_results == {"task_001", "task_002"}
    
    def test_tokenization(self):
        """Test text tokenization and stop word filtering."""
        index = TextIndex()
        
        # Test that stop words are filtered out
        index.add("task_001", "This is a test of the system")
        index.add("task_002", "Test the authentication system")
        
        # Should find both tasks despite stop words
        test_results = index.search("test system")
        assert test_results == {"task_001", "task_002"}
        
        # Stop words alone should not match anything
        stop_word_results = index.search("the is a")
        assert stop_word_results == set()
    
    def test_case_insensitive_search(self):
        """Test that search is case insensitive."""
        index = TextIndex()
        
        index.add("task_001", "IMPLEMENT User Authentication")
        index.add("task_002", "create USER registration")
        
        # Search with different cases
        results1 = index.search("user")
        results2 = index.search("USER")
        results3 = index.search("User")
        
        assert results1 == results2 == results3 == {"task_001", "task_002"}


class TestTaskIndexManager:
    """Test the TaskIndexManager implementation."""
    
    def create_test_task(self, task_id: str, **kwargs) -> Task:
        """Create a test task with default values."""
        defaults = {
            'title': f'Test Task {task_id}',
            'description': f'Description for {task_id}',
            'status': TaskStatus.PENDING,
            'priority': Priority.MEDIUM,
            'tags': ['test'],
            'parent_id': None,
            'child_ids': [],
            'tool_calls': [],
            'metadata': {}
        }
        defaults.update(kwargs)
        
        return Task(id=task_id, **defaults)
    
    def test_task_indexing(self):
        """Test adding and removing tasks from indexes."""
        manager = TaskIndexManager()
        
        task = self.create_test_task(
            "task_001",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            tags=["backend", "auth"]
        )
        
        manager.add_task(task)
        
        # Verify task is in indexes
        assert "task_001" in manager._indexed_tasks
        assert manager.status_index.find_exact("pending") == {"task_001"}
        assert manager.priority_index.find_exact("high") == {"task_001"}
        
        # Remove task
        manager.remove_task("task_001")
        assert "task_001" not in manager._indexed_tasks
        assert manager.status_index.find_exact("pending") == set()
    
    def test_task_updates(self):
        """Test updating tasks in indexes."""
        manager = TaskIndexManager()
        
        task = self.create_test_task("task_001", status=TaskStatus.PENDING)
        manager.add_task(task)
        
        # Update task status
        updated_task = self.create_test_task("task_001", status=TaskStatus.COMPLETED)
        manager.update_task(updated_task)
        
        # Verify indexes are updated
        assert manager.status_index.find_exact("pending") == set()
        assert manager.status_index.find_exact("completed") == {"task_001"}
    
    def test_bulk_operations(self):
        """Test bulk adding tasks."""
        manager = TaskIndexManager()
        
        tasks = {
            "task_001": self.create_test_task("task_001", status=TaskStatus.PENDING),
            "task_002": self.create_test_task("task_002", status=TaskStatus.COMPLETED),
            "task_003": self.create_test_task("task_003", status=TaskStatus.IN_PROGRESS)
        }
        
        manager.bulk_add_tasks(tasks)
        
        assert len(manager._indexed_tasks) == 3
        assert manager.status_index.find_exact("pending") == {"task_001"}
        assert manager.status_index.find_exact("completed") == {"task_002"}
        assert manager.status_index.find_exact("in_progress") == {"task_003"}
    
    def test_text_indexing(self):
        """Test text content indexing."""
        manager = TaskIndexManager()
        
        task = self.create_test_task(
            "task_001",
            title="Implement authentication",
            description="Create secure login system"
        )
        
        manager.add_task(task)
        
        # Test text search
        auth_results = manager.text_index.search("authentication")
        assert auth_results == {"task_001"}
        
        login_results = manager.text_index.search("login")
        assert login_results == {"task_001"}
    
    def test_date_indexing(self):
        """Test date-based indexing."""
        manager = TaskIndexManager()
        
        base_date = datetime.now()
        task = self.create_test_task("task_001")
        task.created_at = base_date
        task.updated_at = base_date + timedelta(hours=1)
        task.due_date = base_date + timedelta(days=7)
        
        manager.add_task(task)
        
        # Test date range queries
        created_results = manager.created_date_index.find_range(
            base_date - timedelta(hours=1),
            base_date + timedelta(hours=1)
        )
        assert created_results == {"task_001"}
    
    def test_index_statistics(self):
        """Test index statistics reporting."""
        manager = TaskIndexManager()
        
        tasks = {
            f"task_{i:03d}": self.create_test_task(f"task_{i:03d}")
            for i in range(10)
        }
        
        manager.bulk_add_tasks(tasks)
        
        stats = manager.get_index_stats()
        assert stats['total_indexed_tasks'] == 10
        assert stats['status_index_size'] == 10
        assert stats['text_index_size'] == 10


class TestQueryOptimizer:
    """Test the QueryOptimizer implementation."""
    
    def create_test_tasks(self) -> dict:
        """Create a set of test tasks for query testing."""
        # Use current date to avoid validation issues
        base_date = datetime.now()
        
        tasks = {}
        
        # Create tasks with different attributes
        for i in range(20):
            status = [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED][i % 3]
            priority = [Priority.LOW, Priority.MEDIUM, Priority.HIGH][i % 3]
            
            task = Task(
                id=f"task_{i:03d}",
                title=f"Task {i} - {'auth' if i < 5 else 'database' if i < 10 else 'frontend'}",
                description=f"Description for task {i}",
                status=status,
                priority=priority,
                tags=[f"tag_{i % 4}", "common"],
                parent_id=f"parent_{i // 5}" if i >= 5 else None,
                child_ids=[],
                created_at=base_date + timedelta(days=i),
                updated_at=base_date + timedelta(days=i, hours=1),
                due_date=base_date + timedelta(days=i + 30) if i % 2 == 0 else None,  # Future dates
                tool_calls=[],
                metadata={}
            )
            tasks[task.id] = task
        
        return tasks
    
    def test_status_filtering(self):
        """Test query optimization with status filtering."""
        manager = TaskIndexManager()
        optimizer = QueryOptimizer(manager)
        
        tasks = self.create_test_tasks()
        manager.bulk_add_tasks(tasks)
        
        # Query for pending tasks
        task_filter = TaskFilter(status=[TaskStatus.PENDING])
        result = optimizer.execute_query(task_filter)
        
        assert isinstance(result, QueryResult)
        assert len(result.task_ids) > 0
        assert 'status_index' in result.indexes_used
        assert result.execution_time_ms >= 0
    
    def test_multiple_filters(self):
        """Test query with multiple filters."""
        manager = TaskIndexManager()
        optimizer = QueryOptimizer(manager)
        
        tasks = self.create_test_tasks()
        manager.bulk_add_tasks(tasks)
        
        # Query with multiple filters
        task_filter = TaskFilter(
            status=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
            priority=[Priority.HIGH],
            tags=["common"]
        )
        
        result = optimizer.execute_query(task_filter)
        
        assert isinstance(result, QueryResult)
        assert 'status_index' in result.indexes_used
        assert 'priority_index' in result.indexes_used
        assert 'tag_index' in result.indexes_used
    
    def test_date_range_filtering(self):
        """Test query with date range filters."""
        manager = TaskIndexManager()
        optimizer = QueryOptimizer(manager)
        
        tasks = self.create_test_tasks()
        manager.bulk_add_tasks(tasks)
        
        base_date = datetime.now()
        task_filter = TaskFilter(
            created_after=base_date + timedelta(days=5),
            created_before=base_date + timedelta(days=15)
        )
        
        result = optimizer.execute_query(task_filter)
        
        assert isinstance(result, QueryResult)
        assert 'created_date_index' in result.indexes_used
        assert len(result.task_ids) > 0
    
    def test_text_search_optimization(self):
        """Test optimized text search."""
        manager = TaskIndexManager()
        optimizer = QueryOptimizer(manager)
        
        tasks = self.create_test_tasks()
        manager.bulk_add_tasks(tasks)
        
        # Test different search modes
        result_all = optimizer.execute_text_search("auth", "all")
        assert isinstance(result_all, QueryResult)
        assert 'text_index' in result_all.indexes_used
        
        result_any = optimizer.execute_text_search("auth database", "any")
        assert len(result_any.task_ids) >= len(result_all.task_ids)
        
        result_prefix = optimizer.execute_text_search("auth", "prefix")
        assert isinstance(result_prefix, QueryResult)
    
    def test_query_plan_generation(self):
        """Test query execution plan generation."""
        manager = TaskIndexManager()
        optimizer = QueryOptimizer(manager)
        
        tasks = self.create_test_tasks()
        manager.bulk_add_tasks(tasks)
        
        task_filter = TaskFilter(
            status=[TaskStatus.PENDING],
            priority=[Priority.HIGH],
            search_text="auth"
        )
        
        plan = optimizer.get_query_plan(task_filter)
        
        assert 'estimated_selectivity' in plan
        assert 'recommended_indexes' in plan
        assert 'execution_order' in plan
        assert len(plan['recommended_indexes']) > 0


class TestQueryResult:
    """Test the QueryResult and pagination functionality."""
    
    def test_query_result_creation(self):
        """Test query result creation."""
        task_ids = {f"task_{i:03d}" for i in range(100)}
        
        result = QueryResult(
            task_ids=task_ids,
            total_count=len(task_ids),
            execution_time_ms=15.5,
            indexes_used=['status_index', 'text_index']
        )
        
        assert len(result.task_ids) == 100
        assert result.total_count == 100
        assert result.execution_time_ms == 15.5
        assert result.indexes_used == ['status_index', 'text_index']
    
    def test_pagination(self):
        """Test result pagination."""
        task_ids = {f"task_{i:03d}" for i in range(100)}
        
        result = QueryResult(
            task_ids=task_ids,
            total_count=len(task_ids),
            execution_time_ms=10.0,
            indexes_used=['status_index']
        )
        
        # Test first page
        page1 = result.paginate(offset=0, limit=20)
        assert isinstance(page1, PaginatedResult)
        assert len(page1.task_ids) == 20
        assert page1.offset == 0
        assert page1.limit == 20
        assert page1.has_more is True
        assert page1.total_count == 100
        
        # Test middle page
        page3 = result.paginate(offset=40, limit=20)
        assert len(page3.task_ids) == 20
        assert page3.offset == 40
        assert page3.has_more is True
        
        # Test last page
        last_page = result.paginate(offset=90, limit=20)
        assert len(last_page.task_ids) == 10  # Only 10 items left
        assert last_page.has_more is False


class TestGlobalIndexManager:
    """Test global index manager functions."""
    
    def test_get_index_manager_singleton(self):
        """Test that get_index_manager returns the same instance."""
        manager1 = get_index_manager()
        manager2 = get_index_manager()
        
        assert manager1 is manager2
        assert isinstance(manager1, TaskIndexManager)
    
    def test_initialize_indexing(self):
        """Test index manager initialization."""
        manager = initialize_indexing()
        
        assert isinstance(manager, TaskIndexManager)
        
        # Should return the same instance
        same_manager = get_index_manager()
        assert same_manager is manager


class TestPerformanceCharacteristics:
    """Test performance characteristics of the indexing system."""
    
    def create_large_dataset(self, size: int) -> dict:
        """Create a large dataset for performance testing."""
        # Use current date to avoid validation issues
        base_date = datetime.now()
        tasks = {}
        
        for i in range(size):
            status = [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED][i % 3]
            priority = [Priority.LOW, Priority.MEDIUM, Priority.HIGH][i % 3]
            
            task = Task(
                id=f"task_{i:05d}",
                title=f"Task {i} - Performance test task",
                description=f"This is a performance test task number {i} with some searchable content",
                status=status,
                priority=priority,
                tags=[f"tag_{i % 10}", f"category_{i % 5}", "performance"],
                parent_id=None,
                child_ids=[],
                created_at=base_date + timedelta(days=i % 365),
                updated_at=base_date + timedelta(days=i % 365, hours=1),
                due_date=base_date + timedelta(days=(i % 365) + 365) if i % 3 == 0 else None,  # Future dates
                tool_calls=[],
                metadata={"index": i}
            )
            tasks[task.id] = task
        
        return tasks
    
    def test_bulk_indexing_performance(self):
        """Test performance of bulk indexing operations."""
        manager = TaskIndexManager()
        tasks = self.create_large_dataset(1000)
        
        start_time = time.time()
        manager.bulk_add_tasks(tasks)
        indexing_time = time.time() - start_time
        
        # Should index 1000 tasks in reasonable time
        assert indexing_time < 5.0  # Less than 5 seconds
        assert len(manager._indexed_tasks) == 1000
        
        # Verify indexes are populated
        stats = manager.get_index_stats()
        assert stats['total_indexed_tasks'] == 1000
        assert stats['status_index_size'] == 1000
        assert stats['text_index_size'] == 1000
    
    def test_query_performance(self):
        """Test query performance on large dataset."""
        manager = TaskIndexManager()
        optimizer = QueryOptimizer(manager)
        
        tasks = self.create_large_dataset(1000)
        manager.bulk_add_tasks(tasks)
        
        # Test various query types
        queries = [
            TaskFilter(status=[TaskStatus.PENDING]),
            TaskFilter(priority=[Priority.HIGH, Priority.MEDIUM]),
            TaskFilter(tags=["performance"]),
            TaskFilter(search_text="performance test"),
            TaskFilter(
                status=[TaskStatus.PENDING],
                priority=[Priority.HIGH],
                tags=["performance"]
            )
        ]
        
        for task_filter in queries:
            start_time = time.time()
            result = optimizer.execute_query(task_filter)
            query_time = time.time() - start_time
            
            # Each query should complete quickly
            assert query_time < 0.5  # Less than 500ms
            assert isinstance(result, QueryResult)
            assert result.execution_time_ms < 500  # Internal timing should also be fast
    
    def test_text_search_performance(self):
        """Test text search performance."""
        manager = TaskIndexManager()
        optimizer = QueryOptimizer(manager)
        
        tasks = self.create_large_dataset(1000)
        manager.bulk_add_tasks(tasks)
        
        # Test different text search operations
        search_queries = [
            ("performance", "all"),
            ("task test", "all"),
            ("performance test content", "any"),
            ("perf", "prefix")
        ]
        
        for query, mode in search_queries:
            start_time = time.time()
            result = optimizer.execute_text_search(query, mode)
            search_time = time.time() - start_time
            
            # Text search should be fast
            assert search_time < 1.0  # Less than 1 second
            assert isinstance(result, QueryResult)
            assert len(result.task_ids) > 0  # Should find some results
    
    def test_index_memory_efficiency(self):
        """Test memory efficiency of indexes."""
        manager = TaskIndexManager()
        
        # Add tasks and measure index growth
        for batch_size in [100, 500, 1000]:
            manager.clear_all_indexes()
            tasks = self.create_large_dataset(batch_size)
            manager.bulk_add_tasks(tasks)
            
            stats = manager.get_index_stats()
            
            # Index sizes should scale linearly with task count
            assert stats['total_indexed_tasks'] == batch_size
            assert stats['status_index_size'] == batch_size
            assert stats['text_index_size'] == batch_size
            
            # All indexes should be populated (except optional ones)
            # parent_index is also optional since not all tasks have parents
            optional_indexes = {'due_date_index_size', 'parent_index_size'}
            assert all(size > 0 for key, size in stats.items() 
                      if key.endswith('_size') and key not in optional_indexes)