"""
Performance and Load Testing for Todo MCP System.

This module provides comprehensive performance and load tests
to verify system performance requirements, memory usage,
and stability under high load conditions.
"""

import asyncio
import json
import time
import tempfile
import pytest
import os
import gc
from pathlib import Path
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
import threading

from src.todo_mcp.config import TodoConfig
from src.todo_mcp.server import TodoMCPServer

# Try to import psutil, but make it optional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@pytest.fixture
def performance_server():
    """Create server optimized for performance testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = TodoConfig(
            data_directory=temp_path / "data",
            backup_enabled=False,  # Disable backup for performance
            file_watch_enabled=False,  # Disable file watching
            log_level="ERROR",  # Minimal logging
            max_cache_size=1000,  # Larger cache for performance
            performance_monitoring=True
        )
        
        config.data_directory.mkdir(parents=True, exist_ok=True)
        (config.data_directory / "tasks").mkdir(exist_ok=True)
        
        server = TodoMCPServer(config)
        # Mock the task service for testing
        from unittest.mock import AsyncMock
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = True
        server.task_service.cleanup = AsyncMock()
        
        yield server


class TestPerformanceRequirements:
    """Test system performance requirements."""
    
    @pytest.mark.asyncio
    async def test_task_creation_performance(self, performance_server):
        """Test task creation performance meets requirements."""
        server = performance_server
        
        # Mock the create_task tool to return success
        from unittest.mock import patch
        with patch('src.todo_mcp.tools.task_tools.create_task') as mock_create:
            mock_create.return_value = {
                "success": True,
                "task": {
                    "id": "perf_test_001",
                    "title": "Performance Test Task",
                    "status": "pending"
                }
            }
            
            # Test single task creation time
            start_time = time.time()
            result = await server._handle_tool_call("create_task", {
                "title": "Performance Test Task",
                "description": "Testing task creation performance",
                "priority": "medium"
            })
            end_time = time.time()
            
            creation_time = end_time - start_time
            data = json.loads(result[0].text)
            
            assert data["success"] is True
            # Task creation should be under 100ms
            assert creation_time < 0.1, f"Task creation took {creation_time:.3f}s, expected < 0.1s"
    
    @pytest.mark.asyncio
    async def test_task_retrieval_performance(self, performance_server):
        """Test task retrieval performance."""
        server = performance_server
        
        # Create a task first
        create_result = await server._handle_tool_call("create_task", {
            "title": "Retrieval Test Task",
            "description": "Testing task retrieval performance"
        })
        create_data = json.loads(create_result[0].text)
        task_id = create_data["task"]["id"]
        
        # Test retrieval time
        start_time = time.time()
        result = await server._handle_tool_call("get_task", {"task_id": task_id})
        end_time = time.time()
        
        retrieval_time = end_time - start_time
        data = json.loads(result[0].text)
        
        assert data["success"] is True
        # Task retrieval should be under 50ms
        assert retrieval_time < 0.05, f"Task retrieval took {retrieval_time:.3f}s, expected < 0.05s"
    
    @pytest.mark.asyncio
    async def test_search_performance(self, performance_server):
        """Test search performance with moderate dataset."""
        server = performance_server
        
        # Create test dataset
        num_tasks = 100
        for i in range(num_tasks):
            await server._handle_tool_call("create_task", {
                "title": f"Search Test Task {i+1}",
                "description": f"Task {i+1} for search performance testing",
                "tags": [f"tag_{i%10}", "search_test"]
            })
        
        # Test search performance
        start_time = time.time()
        result = await server._handle_tool_call("search_tasks", {
            "query": "Search Test",
            "limit": 50
        })
        end_time = time.time()
        
        search_time = end_time - start_time
        data = json.loads(result[0].text)
        
        assert data["success"] is True
        assert len(data["tasks"]) > 0
        # Search should be under 200ms for 100 tasks
        assert search_time < 0.2, f"Search took {search_time:.3f}s, expected < 0.2s"
    
    @pytest.mark.asyncio
    async def test_list_tasks_performance(self, performance_server):
        """Test list tasks performance."""
        server = performance_server
        
        # Create test dataset
        num_tasks = 200
        for i in range(num_tasks):
            await server._handle_tool_call("create_task", {
                "title": f"List Test Task {i+1}",
                "description": f"Task {i+1} for list performance testing"
            })
        
        # Test list performance
        start_time = time.time()
        result = await server._handle_tool_call("list_tasks", {"limit": 100})
        end_time = time.time()
        
        list_time = end_time - start_time
        data = json.loads(result[0].text)
        
        assert data["success"] is True
        assert len(data["tasks"]) == 100
        # List should be under 150ms for 200 tasks
        assert list_time < 0.15, f"List took {list_time:.3f}s, expected < 0.15s"


class TestLoadTesting:
    """Test system behavior under load."""
    
    @pytest.mark.asyncio
    async def test_large_dataset_creation(self, performance_server):
        """Test creating large dataset (1000+ tasks)."""
        server = performance_server
        
        num_tasks = 1000
        batch_size = 50
        
        async def create_task_batch(start_index: int, batch_size: int) -> List[str]:
            """Create a batch of tasks."""
            task_ids = []
            for i in range(batch_size):
                task_index = start_index + i
                result = await server._handle_tool_call("create_task", {
                    "title": f"Load Test Task {task_index:04d}",
                    "description": f"Task {task_index} for load testing",
                    "priority": ["low", "medium", "high"][task_index % 3],
                    "tags": [f"batch_{task_index//100}", "load_test"]
                })
                data = json.loads(result[0].text)
                if data.get("success"):
                    task_ids.append(data["task"]["id"])
            return task_ids
        
        # Create tasks in batches
        start_time = time.time()
        batch_tasks = []
        for i in range(0, num_tasks, batch_size):
            remaining = min(batch_size, num_tasks - i)
            batch_tasks.append(create_task_batch(i, remaining))
        
        batch_results = await asyncio.gather(*batch_tasks)
        end_time = time.time()
        
        # Verify results
        all_task_ids = [task_id for batch in batch_results for task_id in batch]
        creation_time = end_time - start_time
        
        assert len(all_task_ids) == num_tasks
        # Should create 1000 tasks in under 30 seconds
        assert creation_time < 30, f"Creating {num_tasks} tasks took {creation_time:.1f}s, expected < 30s"
        
        # Test operations on large dataset
        stats_start = time.time()
        stats_result = await server._handle_tool_call("get_task_statistics", {})
        stats_end = time.time()
        
        stats_data = json.loads(stats_result[0].text)
        stats_time = stats_end - stats_start
        
        assert stats_data["success"] is True
        assert stats_data["statistics"]["total_tasks"] >= num_tasks
        # Statistics should be fast even with large dataset
        assert stats_time < 1.0, f"Statistics took {stats_time:.3f}s, expected < 1.0s"
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_load(self, performance_server):
        """Test system under concurrent operation load."""
        server = performance_server
        
        # Create initial dataset
        initial_tasks = 100
        task_ids = []
        for i in range(initial_tasks):
            result = await server._handle_tool_call("create_task", {
                "title": f"Concurrent Test Task {i+1}",
                "description": f"Task {i+1} for concurrent load testing"
            })
            data = json.loads(result[0].text)
            if data.get("success"):
                task_ids.append(data["task"]["id"])
        
        async def mixed_operations(operation_id: int) -> Dict[str, bool]:
            """Perform mixed operations concurrently."""
            results = {}
            
            # Create task
            create_result = await server._handle_tool_call("create_task", {
                "title": f"Concurrent Load Task {operation_id}",
                "description": f"Load test operation {operation_id}"
            })
            create_data = json.loads(create_result[0].text)
            results["create"] = create_data.get("success", False)
            
            # Update existing task
            if task_ids:
                task_id = task_ids[operation_id % len(task_ids)]
                update_result = await server._handle_tool_call("update_task_status", {
                    "task_id": task_id,
                    "status": ["pending", "in_progress", "completed"][operation_id % 3]
                })
                update_data = json.loads(update_result[0].text)
                results["update"] = update_data.get("success", False)
            
            # Search operation
            search_result = await server._handle_tool_call("search_tasks", {
                "query": "Concurrent",
                "limit": 10
            })
            search_data = json.loads(search_result[0].text)
            results["search"] = search_data.get("success", False)
            
            # List operation
            list_result = await server._handle_tool_call("list_tasks", {"limit": 20})
            list_data = json.loads(list_result[0].text)
            results["list"] = list_data.get("success", False)
            
            return results
        
        # Run concurrent operations
        num_concurrent = 50
        start_time = time.time()
        
        concurrent_tasks = [
            mixed_operations(i)
            for i in range(num_concurrent)
        ]
        
        operation_results = await asyncio.gather(*concurrent_tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # Analyze results
        success_counts = {"create": 0, "update": 0, "search": 0, "list": 0}
        for result in operation_results:
            for operation, success in result.items():
                if success:
                    success_counts[operation] += 1
        
        # Should handle concurrent load efficiently
        assert total_time < 10, f"Concurrent operations took {total_time:.1f}s, expected < 10s"
        
        # Should have high success rate (>95%)
        for operation, count in success_counts.items():
            success_rate = count / num_concurrent
            assert success_rate > 0.95, f"Low success rate for {operation}: {success_rate:.2%}"
    
    @pytest.mark.asyncio
    async def test_hierarchy_operations_load(self, performance_server):
        """Test hierarchy operations under load."""
        server = performance_server
        
        # Create hierarchical structure
        num_parents = 20
        children_per_parent = 10
        
        parent_ids = []
        for i in range(num_parents):
            result = await server._handle_tool_call("create_task", {
                "title": f"Parent Task {i+1}",
                "description": f"Parent task {i+1} for hierarchy load test"
            })
            data = json.loads(result[0].text)
            parent_ids.append(data["task"]["id"])
        
        # Create children concurrently
        async def create_children_for_parent(parent_id: str, parent_index: int) -> List[str]:
            """Create children for a parent."""
            child_tasks = []
            for i in range(children_per_parent):
                child_task = server._handle_tool_call("create_task", {
                    "title": f"Child Task {parent_index}-{i+1}",
                    "description": f"Child task {i+1} of parent {parent_index}",
                    "parent_id": parent_id
                })
                child_tasks.append(child_task)
            
            results = await asyncio.gather(*child_tasks)
            child_ids = []
            for result in results:
                data = json.loads(result[0].text)
                if data.get("success"):
                    child_ids.append(data["task"]["id"])
            return child_ids
        
        start_time = time.time()
        hierarchy_tasks = [
            create_children_for_parent(parent_id, i)
            for i, parent_id in enumerate(parent_ids)
        ]
        
        all_children = await asyncio.gather(*hierarchy_tasks)
        creation_time = time.time() - start_time
        
        total_children = sum(len(children) for children in all_children)
        expected_children = num_parents * children_per_parent
        
        assert total_children == expected_children
        # Should create hierarchy efficiently
        assert creation_time < 15, f"Hierarchy creation took {creation_time:.1f}s, expected < 15s"
        
        # Test hierarchy retrieval performance
        hierarchy_start = time.time()
        hierarchy_tasks = [
            server._handle_tool_call("get_task_hierarchy", {"root_id": parent_id})
            for parent_id in parent_ids
        ]
        
        hierarchy_results = await asyncio.gather(*hierarchy_tasks)
        hierarchy_time = time.time() - hierarchy_start
        
        # Verify all hierarchies retrieved successfully
        for result in hierarchy_results:
            data = json.loads(result[0].text)
            assert data["success"] is True
            assert len(data["hierarchy"]["children"]) == children_per_parent
        
        # Hierarchy retrieval should be fast
        assert hierarchy_time < 5, f"Hierarchy retrieval took {hierarchy_time:.1f}s, expected < 5s"


class TestMemoryUsage:
    """Test memory usage and stability."""
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        if not PSUTIL_AVAILABLE:
            pytest.skip("psutil not available for memory monitoring")
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, performance_server):
        """Test memory usage remains stable during operations."""
        server = performance_server
        
        initial_memory = self.get_memory_usage()
        
        # Perform many operations to test for memory leaks
        for cycle in range(20):
            # Create tasks
            task_ids = []
            for i in range(20):
                result = await server._handle_tool_call("create_task", {
                    "title": f"Memory Test Task {cycle}-{i}",
                    "description": f"Testing memory stability cycle {cycle}"
                })
                data = json.loads(result[0].text)
                if data.get("success"):
                    task_ids.append(data["task"]["id"])
            
            # Perform operations
            for task_id in task_ids:
                await server._handle_tool_call("update_task_status", {
                    "task_id": task_id,
                    "status": "completed"
                })
                await server._handle_tool_call("get_task", {"task_id": task_id})
            
            # Search operations
            await server._handle_tool_call("search_tasks", {"query": "Memory Test"})
            await server._handle_tool_call("list_tasks", {"limit": 50})
            
            # Clean up
            for task_id in task_ids:
                await server._handle_tool_call("delete_task", {"task_id": task_id})
            
            # Force garbage collection
            gc.collect()
            
            # Check memory usage every 5 cycles
            if cycle % 5 == 0:
                current_memory = self.get_memory_usage()
                memory_increase = current_memory - initial_memory
                
                # Memory increase should be reasonable (< 50MB)
                assert memory_increase < 50, f"Memory increased by {memory_increase:.1f}MB after {cycle} cycles"
        
        final_memory = self.get_memory_usage()
        total_increase = final_memory - initial_memory
        
        # Total memory increase should be minimal
        assert total_increase < 100, f"Total memory increase: {total_increase:.1f}MB"
    
    @pytest.mark.asyncio
    async def test_large_dataset_memory_usage(self, performance_server):
        """Test memory usage with large dataset."""
        server = performance_server
        
        initial_memory = self.get_memory_usage()
        
        # Create large dataset
        num_tasks = 500
        task_ids = []
        
        for i in range(num_tasks):
            result = await server._handle_tool_call("create_task", {
                "title": f"Large Dataset Task {i+1:03d}",
                "description": f"Task {i+1} with longer description for memory testing. " * 5,
                "tags": [f"tag_{i%20}", f"category_{i%10}", "memory_test"]
            })
            data = json.loads(result[0].text)
            if data.get("success"):
                task_ids.append(data["task"]["id"])
        
        dataset_memory = self.get_memory_usage()
        dataset_increase = dataset_memory - initial_memory
        
        # Memory per task should be reasonable (< 1KB per task on average)
        memory_per_task = (dataset_increase * 1024) / len(task_ids)  # Convert to KB
        assert memory_per_task < 1, f"Memory per task: {memory_per_task:.2f}KB, expected < 1KB"
        
        # Perform operations on large dataset
        await server._handle_tool_call("list_tasks", {"limit": 100})
        await server._handle_tool_call("search_tasks", {"query": "Large Dataset"})
        await server._handle_tool_call("get_task_statistics", {})
        
        operations_memory = self.get_memory_usage()
        operations_increase = operations_memory - dataset_memory
        
        # Operations shouldn't significantly increase memory
        assert operations_increase < 20, f"Operations increased memory by {operations_increase:.1f}MB"
    
    @pytest.mark.asyncio
    async def test_concurrent_memory_stability(self, performance_server):
        """Test memory stability under concurrent load."""
        server = performance_server
        
        initial_memory = self.get_memory_usage()
        
        async def memory_stress_operation(operation_id: int) -> bool:
            """Perform operations that might cause memory issues."""
            try:
                # Create task with large description
                large_description = f"Large description for memory stress test. " * 100
                result = await server._handle_tool_call("create_task", {
                    "title": f"Memory Stress Task {operation_id}",
                    "description": large_description,
                    "tags": [f"stress_{operation_id}", "memory_test"]
                })
                data = json.loads(result[0].text)
                
                if data.get("success"):
                    task_id = data["task"]["id"]
                    
                    # Perform multiple operations
                    await server._handle_tool_call("get_task", {"task_id": task_id})
                    await server._handle_tool_call("update_task_status", {
                        "task_id": task_id,
                        "status": "in_progress"
                    })
                    await server._handle_tool_call("search_tasks", {
                        "query": f"Memory Stress Task {operation_id}"
                    })
                    
                    # Clean up
                    await server._handle_tool_call("delete_task", {"task_id": task_id})
                    
                return True
            except Exception:
                return False
        
        # Run concurrent memory stress operations
        num_operations = 100
        stress_tasks = [
            memory_stress_operation(i)
            for i in range(num_operations)
        ]
        
        results = await asyncio.gather(*stress_tasks)
        
        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Most operations should succeed
        success_rate = sum(results) / len(results)
        assert success_rate > 0.95, f"Success rate: {success_rate:.2%}, expected > 95%"
        
        # Memory increase should be reasonable
        assert memory_increase < 100, f"Memory increased by {memory_increase:.1f}MB during stress test"


class TestResponseTimeRequirements:
    """Test response time requirements under various conditions."""
    
    @pytest.mark.asyncio
    async def test_response_times_under_load(self, performance_server):
        """Test response times remain acceptable under load."""
        server = performance_server
        
        # Create background load
        num_background_tasks = 200
        for i in range(num_background_tasks):
            await server._handle_tool_call("create_task", {
                "title": f"Background Task {i+1}",
                "description": f"Background task {i+1} for response time testing"
            })
        
        # Test response times for various operations
        operations = [
            ("create_task", {"title": "Response Time Test", "description": "Testing response time"}),
            ("list_tasks", {"limit": 50}),
            ("search_tasks", {"query": "Background", "limit": 20}),
            ("get_task_statistics", {}),
        ]
        
        response_times = {}
        
        for operation_name, args in operations:
            times = []
            
            # Test each operation multiple times
            for _ in range(10):
                start_time = time.time()
                result = await server._handle_tool_call(operation_name, args)
                end_time = time.time()
                
                data = json.loads(result[0].text)
                assert data.get("success") is True or "statistics" in data
                
                times.append(end_time - start_time)
            
            response_times[operation_name] = {
                "avg": sum(times) / len(times),
                "max": max(times),
                "min": min(times)
            }
        
        # Verify response time requirements
        assert response_times["create_task"]["avg"] < 0.1, "Average create_task time > 100ms"
        assert response_times["list_tasks"]["avg"] < 0.15, "Average list_tasks time > 150ms"
        assert response_times["search_tasks"]["avg"] < 0.2, "Average search_tasks time > 200ms"
        assert response_times["get_task_statistics"]["avg"] < 1.0, "Average statistics time > 1s"
        
        # Max response times should also be reasonable
        for operation, times in response_times.items():
            assert times["max"] < times["avg"] * 3, f"Max time for {operation} is too high"
    
    @pytest.mark.asyncio
    async def test_throughput_requirements(self, performance_server):
        """Test system throughput requirements."""
        server = performance_server
        
        # Test task creation throughput
        num_tasks = 100
        start_time = time.time()
        
        create_tasks = [
            server._handle_tool_call("create_task", {
                "title": f"Throughput Test Task {i+1}",
                "description": f"Task {i+1} for throughput testing"
            })
            for i in range(num_tasks)
        ]
        
        results = await asyncio.gather(*create_tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        throughput = num_tasks / total_time
        
        # Verify all tasks were created successfully
        successful_creates = 0
        for result in results:
            data = json.loads(result[0].text)
            if data.get("success"):
                successful_creates += 1
        
        assert successful_creates == num_tasks
        # Should achieve at least 50 tasks/second throughput
        assert throughput >= 50, f"Throughput: {throughput:.1f} tasks/s, expected >= 50 tasks/s"