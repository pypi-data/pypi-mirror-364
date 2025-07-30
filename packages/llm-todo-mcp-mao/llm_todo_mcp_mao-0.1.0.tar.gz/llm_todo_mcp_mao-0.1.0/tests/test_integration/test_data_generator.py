"""
Test Data Generator for Load Testing.

This module provides utilities to generate large datasets
for performance and load testing scenarios.
"""

import asyncio
import json
import random
from typing import List, Dict, Any
from pathlib import Path

from src.todo_mcp.server import TodoMCPServer


class TestDataGenerator:
    """Generate test data for load testing."""
    
    def __init__(self, server: TodoMCPServer):
        self.server = server
        
        # Sample data for realistic task generation
        self.task_titles = [
            "Fix login authentication bug",
            "Implement user dashboard",
            "Update database schema",
            "Write API documentation",
            "Optimize search performance",
            "Add payment integration",
            "Create user onboarding flow",
            "Implement data backup system",
            "Design mobile responsive layout",
            "Set up monitoring alerts",
            "Refactor legacy code",
            "Add unit tests coverage",
            "Implement caching layer",
            "Update security policies",
            "Create admin panel",
            "Optimize database queries",
            "Add email notifications",
            "Implement file upload",
            "Create reporting dashboard",
            "Add multi-language support"
        ]
        
        self.task_descriptions = [
            "This task involves implementing new functionality to improve user experience.",
            "Critical bug fix that needs to be addressed immediately for system stability.",
            "Performance optimization to reduce response times and improve scalability.",
            "Documentation update to ensure all features are properly documented.",
            "Security enhancement to protect user data and prevent vulnerabilities.",
            "UI/UX improvement to make the interface more intuitive and user-friendly.",
            "Backend infrastructure work to support new features and scale better.",
            "Testing and quality assurance to ensure reliability and prevent regressions.",
            "Integration work to connect different systems and improve workflow.",
            "Maintenance task to keep the system running smoothly and efficiently."
        ]
        
        self.tags = [
            "frontend", "backend", "database", "api", "ui", "ux", "security",
            "performance", "bug", "feature", "documentation", "testing",
            "integration", "maintenance", "optimization", "mobile", "web",
            "admin", "user", "payment", "notification", "monitoring"
        ]
        
        self.priorities = ["low", "medium", "high", "urgent"]
        self.statuses = ["pending", "in_progress", "completed", "blocked"]
    
    async def generate_tasks(self, count: int, with_hierarchy: bool = False) -> List[str]:
        """
        Generate a specified number of tasks.
        
        Args:
            count: Number of tasks to generate
            with_hierarchy: Whether to create hierarchical relationships
            
        Returns:
            List of created task IDs
        """
        task_ids = []
        
        # Generate root tasks first
        root_count = count if not with_hierarchy else max(1, count // 5)
        
        for i in range(root_count):
            task_data = self._generate_task_data(i)
            result = await self.server._handle_tool_call("create_task", task_data)
            data = json.loads(result[0].text)
            
            if data.get("success"):
                task_ids.append(data["task"]["id"])
        
        # Generate child tasks if hierarchy is requested
        if with_hierarchy and len(task_ids) > 0:
            remaining_tasks = count - len(task_ids)
            children_per_parent = max(1, remaining_tasks // len(task_ids))
            
            for parent_id in task_ids[:]:
                for j in range(children_per_parent):
                    if len(task_ids) >= count:
                        break
                    
                    child_data = self._generate_task_data(len(task_ids), parent_id)
                    result = await self.server._handle_tool_call("create_task", child_data)
                    data = json.loads(result[0].text)
                    
                    if data.get("success"):
                        task_ids.append(data["task"]["id"])
        
        return task_ids[:count]
    
    def _generate_task_data(self, index: int, parent_id: str = None) -> Dict[str, Any]:
        """Generate realistic task data."""
        title = random.choice(self.task_titles)
        if parent_id:
            title = f"Subtask: {title}"
        else:
            title = f"{title} #{index + 1}"
        
        description = random.choice(self.task_descriptions)
        if index % 3 == 0:
            # Add longer description for some tasks
            description += f" Additional details for task {index + 1}: " + \
                          "This task requires careful planning and coordination with multiple teams. " + \
                          "Please ensure all stakeholders are informed and requirements are clearly defined."
        
        priority = random.choice(self.priorities)
        selected_tags = random.sample(self.tags, random.randint(1, 4))
        
        task_data = {
            "title": title,
            "description": description,
            "priority": priority,
            "tags": selected_tags
        }
        
        if parent_id:
            task_data["parent_id"] = parent_id
        
        return task_data
    
    async def generate_realistic_dataset(self, size: str = "medium") -> Dict[str, Any]:
        """
        Generate a realistic dataset for testing.
        
        Args:
            size: Dataset size - "small", "medium", "large", or "xlarge"
            
        Returns:
            Dictionary with dataset statistics
        """
        size_configs = {
            "small": {"tasks": 50, "hierarchy": True},
            "medium": {"tasks": 200, "hierarchy": True},
            "large": {"tasks": 1000, "hierarchy": True},
            "xlarge": {"tasks": 5000, "hierarchy": False}  # No hierarchy for very large datasets
        }
        
        config = size_configs.get(size, size_configs["medium"])
        
        print(f"Generating {size} dataset with {config['tasks']} tasks...")
        
        # Generate tasks
        task_ids = await self.generate_tasks(
            config["tasks"], 
            with_hierarchy=config["hierarchy"]
        )
        
        # Update some tasks to different statuses
        status_updates = min(len(task_ids) // 2, 100)  # Update up to 100 tasks
        for i in range(status_updates):
            task_id = random.choice(task_ids)
            status = random.choice(self.statuses)
            
            await self.server._handle_tool_call("update_task_status", {
                "task_id": task_id,
                "status": status
            })
        
        # Get final statistics
        stats_result = await self.server._handle_tool_call("get_task_statistics", {})
        stats_data = json.loads(stats_result[0].text)
        
        return {
            "size": size,
            "tasks_created": len(task_ids),
            "task_ids": task_ids,
            "statistics": stats_data.get("statistics", {}),
            "hierarchy_enabled": config["hierarchy"]
        }
    
    async def cleanup_test_data(self, task_ids: List[str]) -> int:
        """
        Clean up test data by deleting tasks.
        
        Args:
            task_ids: List of task IDs to delete
            
        Returns:
            Number of successfully deleted tasks
        """
        deleted_count = 0
        
        for task_id in task_ids:
            try:
                result = await self.server._handle_tool_call("delete_task", {
                    "task_id": task_id,
                    "cascade": True  # Delete children as well
                })
                data = json.loads(result[0].text)
                
                if data.get("success"):
                    deleted_count += 1
            except Exception:
                # Continue deleting other tasks even if one fails
                continue
        
        return deleted_count


class PerformanceTestScenarios:
    """Pre-defined performance test scenarios."""
    
    def __init__(self, server: TodoMCPServer):
        self.server = server
        self.generator = TestDataGenerator(server)
    
    async def scenario_concurrent_users(self, num_users: int = 10) -> Dict[str, Any]:
        """
        Simulate concurrent users performing various operations.
        
        Args:
            num_users: Number of concurrent users to simulate
            
        Returns:
            Performance metrics
        """
        import time
        
        async def user_session(user_id: int) -> Dict[str, Any]:
            """Simulate a user session with mixed operations."""
            session_results = {
                "user_id": user_id,
                "operations": [],
                "total_time": 0,
                "success_count": 0,
                "error_count": 0
            }
            
            session_start = time.time()
            
            # User creates some tasks
            for i in range(3):
                op_start = time.time()
                result = await self.server._handle_tool_call("create_task", {
                    "title": f"User {user_id} Task {i+1}",
                    "description": f"Task created by user {user_id}",
                    "tags": [f"user_{user_id}"]
                })
                op_end = time.time()
                
                data = json.loads(result[0].text)
                success = data.get("success", False)
                
                session_results["operations"].append({
                    "type": "create_task",
                    "time": op_end - op_start,
                    "success": success
                })
                
                if success:
                    session_results["success_count"] += 1
                else:
                    session_results["error_count"] += 1
            
            # User searches for tasks
            op_start = time.time()
            search_result = await self.server._handle_tool_call("search_tasks", {
                "query": f"User {user_id}",
                "limit": 10
            })
            op_end = time.time()
            
            search_data = json.loads(search_result[0].text)
            search_success = search_data.get("success", False)
            
            session_results["operations"].append({
                "type": "search_tasks",
                "time": op_end - op_start,
                "success": search_success
            })
            
            if search_success:
                session_results["success_count"] += 1
            else:
                session_results["error_count"] += 1
            
            # User lists tasks
            op_start = time.time()
            list_result = await self.server._handle_tool_call("list_tasks", {"limit": 20})
            op_end = time.time()
            
            list_data = json.loads(list_result[0].text)
            list_success = list_data.get("success", False)
            
            session_results["operations"].append({
                "type": "list_tasks",
                "time": op_end - op_start,
                "success": list_success
            })
            
            if list_success:
                session_results["success_count"] += 1
            else:
                session_results["error_count"] += 1
            
            session_results["total_time"] = time.time() - session_start
            return session_results
        
        # Run concurrent user sessions
        start_time = time.time()
        user_tasks = [user_session(i) for i in range(num_users)]
        user_results = await asyncio.gather(*user_tasks)
        total_time = time.time() - start_time
        
        # Aggregate results
        total_operations = sum(len(result["operations"]) for result in user_results)
        total_successes = sum(result["success_count"] for result in user_results)
        total_errors = sum(result["error_count"] for result in user_results)
        
        avg_response_times = {}
        for result in user_results:
            for op in result["operations"]:
                op_type = op["type"]
                if op_type not in avg_response_times:
                    avg_response_times[op_type] = []
                avg_response_times[op_type].append(op["time"])
        
        # Calculate averages
        for op_type in avg_response_times:
            times = avg_response_times[op_type]
            avg_response_times[op_type] = {
                "avg": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
                "count": len(times)
            }
        
        return {
            "scenario": "concurrent_users",
            "num_users": num_users,
            "total_time": total_time,
            "total_operations": total_operations,
            "success_rate": total_successes / total_operations if total_operations > 0 else 0,
            "operations_per_second": total_operations / total_time if total_time > 0 else 0,
            "avg_response_times": avg_response_times,
            "user_results": user_results
        }
    
    async def scenario_bulk_operations(self, batch_size: int = 100) -> Dict[str, Any]:
        """
        Test bulk operations performance.
        
        Args:
            batch_size: Size of bulk operations
            
        Returns:
            Performance metrics
        """
        import time
        
        # Bulk create
        create_start = time.time()
        create_tasks = [
            self.server._handle_tool_call("create_task", {
                "title": f"Bulk Task {i+1}",
                "description": f"Task {i+1} for bulk testing",
                "priority": ["low", "medium", "high"][i % 3]
            })
            for i in range(batch_size)
        ]
        
        create_results = await asyncio.gather(*create_tasks)
        create_time = time.time() - create_start
        
        # Extract task IDs
        task_ids = []
        create_successes = 0
        for result in create_results:
            data = json.loads(result[0].text)
            if data.get("success"):
                task_ids.append(data["task"]["id"])
                create_successes += 1
        
        # Bulk status update
        update_start = time.time()
        update_tasks = [
            self.server._handle_tool_call("update_task_status", {
                "task_id": task_id,
                "status": "completed"
            })
            for task_id in task_ids
        ]
        
        update_results = await asyncio.gather(*update_tasks)
        update_time = time.time() - update_start
        
        update_successes = sum(
            1 for result in update_results
            if json.loads(result[0].text).get("success", False)
        )
        
        # Bulk retrieval
        get_start = time.time()
        get_tasks = [
            self.server._handle_tool_call("get_task", {"task_id": task_id})
            for task_id in task_ids
        ]
        
        get_results = await asyncio.gather(*get_tasks)
        get_time = time.time() - get_start
        
        get_successes = sum(
            1 for result in get_results
            if json.loads(result[0].text).get("success", False)
        )
        
        return {
            "scenario": "bulk_operations",
            "batch_size": batch_size,
            "create": {
                "time": create_time,
                "successes": create_successes,
                "rate": create_successes / create_time if create_time > 0 else 0
            },
            "update": {
                "time": update_time,
                "successes": update_successes,
                "rate": update_successes / update_time if update_time > 0 else 0
            },
            "retrieve": {
                "time": get_time,
                "successes": get_successes,
                "rate": get_successes / get_time if get_time > 0 else 0
            },
            "task_ids": task_ids
        }