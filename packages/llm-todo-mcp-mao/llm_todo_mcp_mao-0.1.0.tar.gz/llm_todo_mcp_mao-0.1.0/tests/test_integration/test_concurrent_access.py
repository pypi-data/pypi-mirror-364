"""
Concurrent Access Integration Tests.

This module tests multi-agent concurrent access scenarios,
ensuring thread safety and data consistency under concurrent load.
"""

import asyncio
import json
import pytest
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import threading
import time

from src.todo_mcp.config import TodoConfig
from src.todo_mcp.server import TodoMCPServer


@pytest.fixture
async def concurrent_server():
    """Create server for concurrent testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = TodoConfig(
            data_directory=temp_path / "data",
            backup_enabled=False,
            file_watch_enabled=False,
            log_level="WARNING"  # Reduce log noise
        )
        
        config.data_directory.mkdir(parents=True, exist_ok=True)
        (config.data_directory / "tasks").mkdir(exist_ok=True)
        
        server = TodoMCPServer(config)
        await server.task_service.initialize()
        yield server
        await server.task_service.cleanup()


class TestConcurrentTaskOperations:
    """Test concurrent task operations."""
    
    @pytest.mark.asyncio
    async def test_concurrent_task_creation(self, concurrent_server):
        """Test concurrent task creation from multiple agents."""
        server = concurrent_server
        
        async def create_task_batch(agent_id: int, batch_size: int) -> List[str]:
            """Create a batch of tasks for one agent."""
            task_ids = []
            for i in range(batch_size):
                result = await server._handle_tool_call("create_task", {
                    "title": f"Agent {agent_id} Task {i+1}",
                    "description": f"Task created by agent {agent_id}",
                    "priority": ["low", "medium", "high"][i % 3],
                    "tags": [f"agent_{agent_id}", "concurrent"]
                })
                
                data = json.loads(result[0].text)
                if data.get("success"):
                    task_ids.append(data["task"]["id"])
                    
            return task_ids
        
        # Simulate 5 agents creating 10 tasks each concurrently
        num_agents = 5
        tasks_per_agent = 10
        
        agent_tasks = await asyncio.gather(*[
            create_task_batch(agent_id, tasks_per_agent)
            for agent_id in range(num_agents)
        ])
        
        # Verify all tasks were created
        all_task_ids = [task_id for batch in agent_tasks for task_id in batch]
        assert len(all_task_ids) == num_agents * tasks_per_agent
        
        # Verify all task IDs are unique
        assert len(set(all_task_ids)) == len(all_task_ids)
        
        # Verify all tasks exist and are accessible
        for task_id in all_task_ids:
            result = await server._handle_tool_call("get_task", {"task_id": task_id})
            data = json.loads(result[0].text)
            assert data["success"] is True
            assert data["task"]["id"] == task_id
    
    @pytest.mark.asyncio
    async def test_concurrent_status_updates(self, concurrent_server):
        """Test concurrent status updates on different tasks."""
        server = concurrent_server
        
        # Create tasks first
        task_ids = []
        for i in range(20):
            result = await server._handle_tool_call("create_task", {
                "title": f"Status Test Task {i+1}",
                "description": "Task for concurrent status testing"
            })
            data = json.loads(result[0].text)
            task_ids.append(data["task"]["id"])
        
        async def update_task_status_batch(task_batch: List[str], status: str) -> List[bool]:
            """Update status for a batch of tasks."""
            results = []
            for task_id in task_batch:
                result = await server._handle_tool_call("update_task_status", {
                    "task_id": task_id,
                    "status": status
                })
                data = json.loads(result[0].text)
                results.append(data.get("success", False))
            return results
        
        # Split tasks into batches and update concurrently
        batch_size = 5
        statuses = ["in_progress", "completed", "blocked", "pending"]
        
        update_tasks = []
        for i in range(0, len(task_ids), batch_size):
            batch = task_ids[i:i+batch_size]
            status = statuses[i // batch_size % len(statuses)]
            update_tasks.append(update_task_status_batch(batch, status))
        
        batch_results = await asyncio.gather(*update_tasks)
        
        # Verify all updates succeeded
        all_results = [result for batch in batch_results for result in batch]
        assert all(all_results), "Some status updates failed"
        
        # Verify final states
        for i, task_id in enumerate(task_ids):
            result = await server._handle_tool_call("get_task", {"task_id": task_id})
            data = json.loads(result[0].text)
            expected_status = statuses[i // batch_size % len(statuses)]
            assert data["task"]["status"] == expected_status
    
    @pytest.mark.asyncio
    async def test_concurrent_hierarchy_operations(self, concurrent_server):
        """Test concurrent hierarchy operations."""
        server = concurrent_server
        
        # Create parent tasks
        parent_ids = []
        for i in range(3):
            result = await server._handle_tool_call("create_task", {
                "title": f"Parent Task {i+1}",
                "description": f"Parent for concurrent hierarchy test"
            })
            data = json.loads(result[0].text)
            parent_ids.append(data["task"]["id"])
        
        async def create_child_hierarchy(parent_id: str, child_count: int) -> List[str]:
            """Create child tasks for a parent concurrently."""
            child_tasks = []
            for i in range(child_count):
                child_task = server._handle_tool_call("create_task", {
                    "title": f"Child Task {i+1}",
                    "description": f"Child task {i+1}",
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
        
        # Create children for all parents concurrently
        children_per_parent = 5
        hierarchy_tasks = [
            create_child_hierarchy(parent_id, children_per_parent)
            for parent_id in parent_ids
        ]
        
        all_children = await asyncio.gather(*hierarchy_tasks)
        
        # Verify hierarchies
        for i, parent_id in enumerate(parent_ids):
            result = await server._handle_tool_call("get_task_hierarchy", {
                "root_id": parent_id
            })
            data = json.loads(result[0].text)
            assert data["success"] is True
            assert len(data["hierarchy"]["children"]) == children_per_parent
            
            # Verify child IDs match
            hierarchy_child_ids = [child["id"] for child in data["hierarchy"]["children"]]
            expected_child_ids = all_children[i]
            assert set(hierarchy_child_ids) == set(expected_child_ids)
    
    @pytest.mark.asyncio
    async def test_concurrent_search_operations(self, concurrent_server):
        """Test concurrent search and filter operations."""
        server = concurrent_server
        
        # Create diverse test data
        test_tasks = []
        categories = ["frontend", "backend", "database", "api", "ui"]
        priorities = ["low", "medium", "high", "urgent"]
        
        for i in range(50):
            category = categories[i % len(categories)]
            priority = priorities[i % len(priorities)]
            
            result = await server._handle_tool_call("create_task", {
                "title": f"{category.title()} Task {i+1}",
                "description": f"Task for {category} development",
                "priority": priority,
                "tags": [category, "test"]
            })
            data = json.loads(result[0].text)
            if data.get("success"):
                test_tasks.append(data["task"]["id"])
        
        # Perform concurrent searches
        search_operations = [
            ("search_tasks", {"query": "Frontend"}),
            ("search_tasks", {"query": "Backend"}),
            ("search_tasks", {"query": "Database"}),
            ("filter_tasks", {"priority": ["high", "urgent"]}),
            ("filter_tasks", {"tags": ["frontend"]}),
            ("filter_tasks", {"tags": ["backend"]}),
            ("get_task_statistics", {}),
            ("get_pending_tasks", {}),
            ("list_tasks", {"limit": 100}),
        ]
        
        # Execute all searches concurrently
        search_tasks = [
            server._handle_tool_call(tool_name, args)
            for tool_name, args in search_operations
        ]
        
        results = await asyncio.gather(*search_tasks)
        
        # Verify all searches completed successfully
        for i, result in enumerate(results):
            assert len(result) == 1
            data = json.loads(result[0].text)
            assert data.get("success") is True or "statistics" in data
            
            # Verify search results make sense
            tool_name, args = search_operations[i]
            if tool_name == "search_tasks":
                assert "tasks" in data
                assert isinstance(data["tasks"], list)
            elif tool_name == "filter_tasks":
                assert "tasks" in data
                assert isinstance(data["tasks"], list)
            elif tool_name == "get_task_statistics":
                assert "statistics" in data
                assert data["statistics"]["total_tasks"] >= len(test_tasks)


class TestDataConsistency:
    """Test data consistency under concurrent access."""
    
    @pytest.mark.asyncio
    async def test_task_update_consistency(self, concurrent_server):
        """Test that concurrent updates maintain data consistency."""
        server = concurrent_server
        
        # Create a task
        result = await server._handle_tool_call("create_task", {
            "title": "Consistency Test Task",
            "description": "Original description",
            "priority": "medium",
            "tags": ["original"]
        })
        data = json.loads(result[0].text)
        task_id = data["task"]["id"]
        
        async def update_task_field(field: str, value: Any, delay: float = 0) -> bool:
            """Update a specific field of the task."""
            if delay > 0:
                await asyncio.sleep(delay)
            
            result = await server._handle_tool_call("update_task", {
                "task_id": task_id,
                field: value
            })
            data = json.loads(result[0].text)
            return data.get("success", False)
        
        # Perform concurrent updates to different fields
        update_operations = [
            update_task_field("description", "Updated description 1", 0.1),
            update_task_field("priority", "high", 0.05),
            update_task_field("tags", ["updated", "concurrent"], 0.15),
            update_task_field("description", "Updated description 2", 0.2),
        ]
        
        results = await asyncio.gather(*update_operations)
        
        # All updates should succeed (last writer wins)
        assert all(results)
        
        # Verify final state is consistent
        final_result = await server._handle_tool_call("get_task", {"task_id": task_id})
        final_data = json.loads(final_result[0].text)
        
        assert final_data["success"] is True
        task = final_data["task"]
        
        # Should have the last written values
        assert task["priority"] == "high"
        assert "updated" in task["tags"]
        assert "concurrent" in task["tags"]
        # Description should be one of the updated versions
        assert "Updated description" in task["description"]
    
    @pytest.mark.asyncio
    async def test_hierarchy_consistency(self, concurrent_server):
        """Test hierarchy consistency under concurrent modifications."""
        server = concurrent_server
        
        # Create parent and child tasks
        parent_result = await server._handle_tool_call("create_task", {
            "title": "Hierarchy Parent",
            "description": "Parent task for consistency test"
        })
        parent_data = json.loads(parent_result[0].text)
        parent_id = parent_data["task"]["id"]
        
        # Create multiple children
        child_ids = []
        for i in range(5):
            result = await server._handle_tool_call("create_task", {
                "title": f"Child Task {i+1}",
                "description": f"Child task {i+1}",
                "parent_id": parent_id
            })
            data = json.loads(result[0].text)
            child_ids.append(data["task"]["id"])
        
        async def move_task_operation(task_id: str, new_parent_id: str = None) -> bool:
            """Move a task to a new parent."""
            result = await server._handle_tool_call("move_task", {
                "task_id": task_id,
                "new_parent_id": new_parent_id
            })
            data = json.loads(result[0].text)
            return data.get("success", False)
        
        # Create another parent
        new_parent_result = await server._handle_tool_call("create_task", {
            "title": "New Parent",
            "description": "Alternative parent"
        })
        new_parent_data = json.loads(new_parent_result[0].text)
        new_parent_id = new_parent_data["task"]["id"]
        
        # Perform concurrent move operations
        move_operations = [
            move_task_operation(child_ids[0], new_parent_id),
            move_task_operation(child_ids[1], new_parent_id),
            move_task_operation(child_ids[2], None),  # Move to root
        ]
        
        results = await asyncio.gather(*move_operations)
        assert all(results)
        
        # Verify hierarchy consistency
        original_hierarchy = await server._handle_tool_call("get_task_hierarchy", {
            "root_id": parent_id
        })
        original_data = json.loads(original_hierarchy[0].text)
        
        new_hierarchy = await server._handle_tool_call("get_task_hierarchy", {
            "root_id": new_parent_id
        })
        new_data = json.loads(new_hierarchy[0].text)
        
        # Original parent should have 2 children left
        assert len(original_data["hierarchy"]["children"]) == 2
        
        # New parent should have 2 children
        assert len(new_data["hierarchy"]["children"]) == 2
        
        # Verify moved tasks are in correct hierarchies
        original_child_ids = [child["id"] for child in original_data["hierarchy"]["children"]]
        new_child_ids = [child["id"] for child in new_data["hierarchy"]["children"]]
        
        assert child_ids[0] in new_child_ids
        assert child_ids[1] in new_child_ids
        assert child_ids[3] in original_child_ids
        assert child_ids[4] in original_child_ids


class TestConcurrentFileOperations:
    """Test concurrent file system operations."""
    
    @pytest.mark.asyncio
    async def test_concurrent_file_creation(self, concurrent_server):
        """Test concurrent file creation and modification."""
        server = concurrent_server
        config = server.config
        
        async def create_and_modify_task(task_index: int) -> str:
            """Create a task and immediately modify it."""
            # Create task
            create_result = await server._handle_tool_call("create_task", {
                "title": f"File Test Task {task_index}",
                "description": f"Original description {task_index}"
            })
            create_data = json.loads(create_result[0].text)
            task_id = create_data["task"]["id"]
            
            # Immediately update it
            await server._handle_tool_call("update_task", {
                "task_id": task_id,
                "description": f"Updated description {task_index}"
            })
            
            return task_id
        
        # Create and modify tasks concurrently
        num_tasks = 10
        task_operations = [
            create_and_modify_task(i)
            for i in range(num_tasks)
        ]
        
        task_ids = await asyncio.gather(*task_operations)
        
        # Verify all files exist and have correct content
        task_files = list((config.data_directory / "tasks").glob("*.md"))
        assert len(task_files) >= num_tasks
        
        # Verify each task file contains updated content
        for task_id in task_ids:
            task_found = False
            for file_path in task_files:
                content = file_path.read_text(encoding='utf-8')
                if task_id in content:
                    assert "Updated description" in content
                    task_found = True
                    break
            assert task_found, f"Task file not found for {task_id}"
    
    @pytest.mark.asyncio
    async def test_concurrent_file_deletion(self, concurrent_server):
        """Test concurrent file deletion operations."""
        server = concurrent_server
        config = server.config
        
        # Create tasks first
        task_ids = []
        for i in range(15):
            result = await server._handle_tool_call("create_task", {
                "title": f"Delete Test Task {i+1}",
                "description": "Task for deletion testing"
            })
            data = json.loads(result[0].text)
            task_ids.append(data["task"]["id"])
        
        # Get initial file count
        initial_files = list((config.data_directory / "tasks").glob("*.md"))
        initial_count = len(initial_files)
        
        async def delete_task_batch(task_batch: List[str]) -> List[bool]:
            """Delete a batch of tasks."""
            results = []
            for task_id in task_batch:
                result = await server._handle_tool_call("delete_task", {"task_id": task_id})
                data = json.loads(result[0].text)
                results.append(data.get("success", False))
            return results
        
        # Delete tasks in batches concurrently
        batch_size = 5
        delete_operations = []
        for i in range(0, len(task_ids), batch_size):
            batch = task_ids[i:i+batch_size]
            delete_operations.append(delete_task_batch(batch))
        
        batch_results = await asyncio.gather(*delete_operations)
        
        # Verify all deletions succeeded
        all_results = [result for batch in batch_results for result in batch]
        assert all(all_results)
        
        # Verify files were actually deleted
        final_files = list((config.data_directory / "tasks").glob("*.md"))
        final_count = len(final_files)
        
        assert final_count == initial_count - len(task_ids)
        
        # Verify tasks are no longer accessible
        for task_id in task_ids:
            result = await server._handle_tool_call("get_task", {"task_id": task_id})
            data = json.loads(result[0].text)
            assert data.get("success") is False or "error" in data


class TestStressConditions:
    """Test system behavior under stress conditions."""
    
    @pytest.mark.asyncio
    async def test_high_concurrency_stress(self, concurrent_server):
        """Test system under high concurrency stress."""
        server = concurrent_server
        
        async def stress_operation(operation_id: int) -> Dict[str, Any]:
            """Perform a mixed set of operations."""
            results = {}
            
            # Create task
            create_result = await server._handle_tool_call("create_task", {
                "title": f"Stress Task {operation_id}",
                "description": f"Stress test operation {operation_id}",
                "priority": ["low", "medium", "high"][operation_id % 3]
            })
            create_data = json.loads(create_result[0].text)
            results["create"] = create_data.get("success", False)
            
            if results["create"]:
                task_id = create_data["task"]["id"]
                
                # Update status
                status_result = await server._handle_tool_call("update_task_status", {
                    "task_id": task_id,
                    "status": "in_progress"
                })
                status_data = json.loads(status_result[0].text)
                results["status_update"] = status_data.get("success", False)
                
                # Search for task
                search_result = await server._handle_tool_call("search_tasks", {
                    "query": f"Stress Task {operation_id}"
                })
                search_data = json.loads(search_result[0].text)
                results["search"] = search_data.get("success", False)
                
                # Get task
                get_result = await server._handle_tool_call("get_task", {"task_id": task_id})
                get_data = json.loads(get_result[0].text)
                results["get"] = get_data.get("success", False)
            
            return results
        
        # Run high number of concurrent operations
        num_operations = 50
        stress_tasks = [
            stress_operation(i)
            for i in range(num_operations)
        ]
        
        operation_results = await asyncio.gather(*stress_tasks)
        
        # Analyze results
        success_counts = {
            "create": 0,
            "status_update": 0,
            "search": 0,
            "get": 0
        }
        
        for result in operation_results:
            for operation, success in result.items():
                if success:
                    success_counts[operation] += 1
        
        # Should have high success rate (>90%)
        for operation, count in success_counts.items():
            success_rate = count / num_operations
            assert success_rate > 0.9, f"Low success rate for {operation}: {success_rate}"
        
        # Verify system is still responsive
        final_stats = await server._handle_tool_call("get_task_statistics", {})
        final_data = json.loads(final_stats[0].text)
        assert final_data.get("success") is True or "statistics" in final_data