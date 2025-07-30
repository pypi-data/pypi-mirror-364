"""
Tests for hierarchy service and HierarchyNode model.

This module contains comprehensive tests for the hierarchy management
functionality, including node operations, cycle detection, and validation.
"""

import pytest
from datetime import datetime, timezone
from typing import List

from src.todo_mcp.models.task import Task
from src.todo_mcp.models.status import TaskStatus, Priority
from src.todo_mcp.services.hierarchy_service import HierarchyNode, HierarchyService
from src.todo_mcp.config import TodoConfig


class TestHierarchyNode:
    """Test cases for HierarchyNode model."""
    
    def create_test_task(self, task_id: str, title: str = "Test Task", parent_id: str = None, child_ids: List[str] = None) -> Task:
        """Helper method to create test tasks."""
        return Task(
            id=task_id,
            title=title,
            description=f"Description for {title}",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            parent_id=parent_id,
            child_ids=child_ids or []
        )
    
    def build_test_hierarchy(self, task_definitions: List[tuple]) -> dict:
        """
        Helper method to build test hierarchies properly.
        
        Args:
            task_definitions: List of tuples (task_id, title, parent_id, child_ids)
        
        Returns:
            Dictionary mapping task_id to HierarchyNode
        """
        # Create all tasks first
        tasks = {}
        for task_id, title, parent_id, child_ids in task_definitions:
            tasks[task_id] = self.create_test_task(task_id, title, parent_id, child_ids)
        
        # Create all nodes
        nodes = {}
        for task_id, task in tasks.items():
            nodes[task_id] = HierarchyNode(task=task)
        
        # Establish relationships
        for task_id, task in tasks.items():
            node = nodes[task_id]
            
            # Set parent relationship
            if task.parent_id and task.parent_id in nodes:
                node.parent = nodes[task.parent_id]
            
            # Set child relationships
            for child_id in task.child_ids:
                if child_id in nodes:
                    if nodes[child_id] not in node.children:
                        node.children.append(nodes[child_id])
        
        return nodes
    
    def test_hierarchy_node_creation(self):
        """Test basic HierarchyNode creation."""
        task = self.create_test_task("task1", "Root Task")
        node = HierarchyNode(task=task)
        
        assert node.task.id == "task1"
        assert node.task.title == "Root Task"
        assert node.parent is None
        assert len(node.children) == 0
    
    def test_hierarchy_node_with_parent_child(self):
        """Test HierarchyNode with parent-child relationships."""
        parent_task = self.create_test_task("parent", "Parent Task", child_ids=["child"])
        child_task = self.create_test_task("child", "Child Task", parent_id="parent")
        
        # Create nodes separately first
        parent_node = HierarchyNode(task=parent_task)
        child_node = HierarchyNode(task=child_task)
        
        # Then establish relationships
        child_node.parent = parent_node
        parent_node.children = [child_node]
        
        assert child_node.parent == parent_node
        assert parent_node.children[0] == child_node
        assert child_node.task.parent_id == "parent"
        assert parent_node.task.child_ids == ["child"]
    
    def test_validate_children_removes_duplicates(self):
        """Test that duplicate children are removed during validation."""
        task1 = self.create_test_task("task1")
        task2 = self.create_test_task("task2")
        
        node1 = HierarchyNode(task=task1)
        node2 = HierarchyNode(task=task2)
        
        # Create parent with duplicate children
        parent_task = self.create_test_task("parent", child_ids=["task1", "task2"])
        parent_node = HierarchyNode(task=parent_task, children=[node1, node2, node1])  # Duplicate node1
        
        # Should only have 2 unique children
        assert len(parent_node.children) == 2
        assert node1 in parent_node.children
        assert node2 in parent_node.children
    
    def test_validate_hierarchy_constraints_parent_mismatch(self):
        """Test validation fails when parent task ID doesn't match parent node."""
        parent_task = self.create_test_task("parent")
        child_task = self.create_test_task("child", parent_id="different_parent")
        
        parent_node = HierarchyNode(task=parent_task)
        
        with pytest.raises(ValueError, match="Task parent_id .* doesn't match parent node task ID"):
            HierarchyNode(task=child_task, parent=parent_node)
    
    def test_validate_hierarchy_constraints_child_mismatch(self):
        """Test validation fails when child IDs don't match child nodes."""
        parent_task = self.create_test_task("parent", child_ids=["child1", "child2"])
        child_task = self.create_test_task("child1", parent_id="parent")
        
        parent_node = HierarchyNode(task=parent_task)
        child_node = HierarchyNode(task=child_task)
        child_node.parent = parent_node
        
        # Only one child node but task has two child IDs - this should fail full validation
        parent_node.children = [child_node]
        
        # Use the full hierarchy validation method instead
        assert not parent_node.validate_full_hierarchy()
    
    def test_prevent_self_referencing_parent(self):
        """Test that self-referencing parent is prevented."""
        task = self.create_test_task("task1")
        node = HierarchyNode(task=task)
        
        # Manually set self-reference (bypassing normal validation)
        node.parent = node
        
        # Should fail hierarchy validation
        assert not node.validate_hierarchy()
    
    def test_prevent_self_referencing_child(self):
        """Test that self-referencing child is prevented."""
        # Task model already prevents self-referencing in child_ids, so test the node level
        task = self.create_test_task("task1")
        node = HierarchyNode(task=task)
        
        # Manually set self-reference (bypassing normal validation)
        node.children = [node]
        
        # Should fail hierarchy validation
        assert not node.validate_hierarchy()
    
    def test_get_ancestors(self):
        """Test getting ancestor nodes."""
        # Create a 3-level hierarchy: grandparent -> parent -> child
        grandparent_task = self.create_test_task("grandparent", child_ids=["parent"])
        parent_task = self.create_test_task("parent", parent_id="grandparent", child_ids=["child"])
        child_task = self.create_test_task("child", parent_id="parent")
        
        # Create nodes separately first
        grandparent_node = HierarchyNode(task=grandparent_task)
        parent_node = HierarchyNode(task=parent_task)
        child_node = HierarchyNode(task=child_task)
        
        # Then establish relationships
        parent_node.parent = grandparent_node
        child_node.parent = parent_node
        grandparent_node.children = [parent_node]
        parent_node.children = [child_node]
        
        ancestors = child_node.get_ancestors()
        assert len(ancestors) == 2
        assert ancestors[0] == parent_node
        assert ancestors[1] == grandparent_node
    
    def test_get_descendants(self):
        """Test getting descendant nodes."""
        # Create hierarchy: parent -> child1, child2 -> grandchild
        nodes = self.build_test_hierarchy([
            ("parent", "Parent", None, ["child1", "child2"]),
            ("child1", "Child1", "parent", ["grandchild"]),
            ("child2", "Child2", "parent", []),
            ("grandchild", "Grandchild", "child1", [])
        ])
        
        parent_node = nodes["parent"]
        child1_node = nodes["child1"]
        child2_node = nodes["child2"]
        grandchild_node = nodes["grandchild"]
        
        descendants = parent_node.get_descendants()
        assert len(descendants) == 3
        assert child1_node in descendants
        assert child2_node in descendants
        assert grandchild_node in descendants
    
    def test_get_root(self):
        """Test getting root node."""
        # Create hierarchy: root -> parent -> child
        nodes = self.build_test_hierarchy([
            ("root", "Root", None, ["parent"]),
            ("parent", "Parent", "root", ["child"]),
            ("child", "Child", "parent", [])
        ])
        
        root_node = nodes["root"]
        parent_node = nodes["parent"]
        child_node = nodes["child"]
        
        assert child_node.get_root() == root_node
        assert parent_node.get_root() == root_node
        assert root_node.get_root() == root_node
    
    def test_get_depth(self):
        """Test getting node depth."""
        # Create hierarchy: root -> parent -> child
        nodes = self.build_test_hierarchy([
            ("root", "Root", None, ["parent"]),
            ("parent", "Parent", "root", ["child"]),
            ("child", "Child", "parent", [])
        ])
        
        root_node = nodes["root"]
        parent_node = nodes["parent"]
        child_node = nodes["child"]
        
        assert root_node.get_depth() == 0
        assert parent_node.get_depth() == 1
        assert child_node.get_depth() == 2
    
    def test_get_sibling_nodes(self):
        """Test getting sibling nodes."""
        nodes = self.build_test_hierarchy([
            ("parent", "Parent", None, ["child1", "child2", "child3"]),
            ("child1", "Child1", "parent", []),
            ("child2", "Child2", "parent", []),
            ("child3", "Child3", "parent", [])
        ])
        
        child1_node = nodes["child1"]
        child2_node = nodes["child2"]
        child3_node = nodes["child3"]
        
        siblings = child1_node.get_sibling_nodes()
        assert len(siblings) == 2
        assert child2_node in siblings
        assert child3_node in siblings
        assert child1_node not in siblings
    
    def test_is_ancestor_of(self):
        """Test ancestor relationship checking."""
        # Create hierarchy: grandparent -> parent -> child
        nodes = self.build_test_hierarchy([
            ("grandparent", "Grandparent", None, ["parent"]),
            ("parent", "Parent", "grandparent", ["child"]),
            ("child", "Child", "parent", [])
        ])
        
        grandparent_node = nodes["grandparent"]
        parent_node = nodes["parent"]
        child_node = nodes["child"]
        
        assert grandparent_node.is_ancestor_of(child_node)
        assert parent_node.is_ancestor_of(child_node)
        assert not child_node.is_ancestor_of(parent_node)
    
    def test_is_descendant_of(self):
        """Test descendant relationship checking."""
        # Create hierarchy: grandparent -> parent -> child
        nodes = self.build_test_hierarchy([
            ("grandparent", "Grandparent", None, ["parent"]),
            ("parent", "Parent", "grandparent", ["child"]),
            ("child", "Child", "parent", [])
        ])
        
        grandparent_node = nodes["grandparent"]
        parent_node = nodes["parent"]
        child_node = nodes["child"]
        
        assert child_node.is_descendant_of(grandparent_node)
        assert child_node.is_descendant_of(parent_node)
        assert not parent_node.is_descendant_of(child_node)
    
    def test_validate_hierarchy_detects_cycles(self):
        """Test that validate_hierarchy detects cycles."""
        # This test is tricky because Pydantic validation prevents cycles during construction
        # We'll test the validation method directly
        task1 = self.create_test_task("task1")
        task2 = self.create_test_task("task2")
        
        node1 = HierarchyNode(task=task1)
        node2 = HierarchyNode(task=task2)
        
        # Manually create a cycle (bypassing Pydantic validation)
        node1.parent = node2
        node2.parent = node1
        
        assert not node1.validate_hierarchy()
        assert not node2.validate_hierarchy()
    
    def test_add_child_node(self):
        """Test adding child node."""
        parent_task = self.create_test_task("parent")
        child_task = self.create_test_task("child")
        
        parent_node = HierarchyNode(task=parent_task)
        child_node = HierarchyNode(task=child_task)
        
        parent_node.add_child_node(child_node)
        
        assert child_node in parent_node.children
        assert child_node.parent == parent_node
        assert "child" in parent_node.task.child_ids
        assert child_node.task.parent_id == "parent"
    
    def test_add_child_node_prevents_cycles(self):
        """Test that adding child node prevents cycles."""
        # Create hierarchy: grandparent -> parent
        nodes = self.build_test_hierarchy([
            ("grandparent", "Grandparent", None, ["parent"]),
            ("parent", "Parent", "grandparent", [])
        ])
        
        grandparent_node = nodes["grandparent"]
        parent_node = nodes["parent"]
        
        # Try to add grandparent as child of parent (would create cycle)
        with pytest.raises(ValueError, match="Cannot add child .* would create a cycle"):
            parent_node.add_child_node(grandparent_node)
    
    def test_remove_child_node(self):
        """Test removing child node."""
        nodes = self.build_test_hierarchy([
            ("parent", "Parent", None, ["child"]),
            ("child", "Child", "parent", [])
        ])
        
        parent_node = nodes["parent"]
        child_node = nodes["child"]
        
        result = parent_node.remove_child_node("child")
        
        assert result is True
        assert child_node not in parent_node.children
        assert child_node.parent is None
        assert "child" not in parent_node.task.child_ids
        assert child_node.task.parent_id is None
    
    def test_remove_child_node_not_found(self):
        """Test removing non-existent child node."""
        parent_task = self.create_test_task("parent")
        parent_node = HierarchyNode(task=parent_task)
        
        result = parent_node.remove_child_node("nonexistent")
        assert result is False
    
    def test_to_dict(self):
        """Test converting node to dictionary."""
        nodes = self.build_test_hierarchy([
            ("parent", "Parent", None, ["child"]),
            ("child", "Child", "parent", [])
        ])
        
        parent_node = nodes["parent"]
        
        result = parent_node.to_dict()
        
        assert result["task"]["id"] == "parent"
        assert result["depth"] == 0
        assert result["has_parent"] is False
        assert result["child_count"] == 1
        assert len(result["children"]) == 1
        assert result["children"][0]["task"]["id"] == "child"
    
    def test_to_dict_max_depth(self):
        """Test converting node to dictionary with max depth limit."""
        # Create 3-level hierarchy
        nodes = self.build_test_hierarchy([
            ("root", "Root", None, ["parent"]),
            ("parent", "Parent", "root", ["child"]),
            ("child", "Child", "parent", [])
        ])
        
        root_node = nodes["root"]
        
        # Test with max_depth=1
        result = root_node.to_dict(max_depth=1)
        
        assert len(result["children"]) == 1
        assert "children" not in result["children"][0]  # Should not include grandchildren


class TestHierarchyService:
    """Test cases for HierarchyService."""
    
    def create_test_config(self) -> TodoConfig:
        """Helper method to create test configuration."""
        from pathlib import Path
        return TodoConfig(
            data_directory=Path("test_data"),
            max_cache_size=100,
            file_watch_enabled=False,
            backup_enabled=False,
            log_level="INFO",
            performance_monitoring=False
        )
    
    def create_test_task(self, task_id: str, title: str = "Test Task", parent_id: str = None, child_ids: List[str] = None) -> Task:
        """Helper method to create test tasks."""
        return Task(
            id=task_id,
            title=title,
            description=f"Description for {title}",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            parent_id=parent_id,
            child_ids=child_ids or []
        )
    
    def test_hierarchy_service_initialization(self):
        """Test HierarchyService initialization."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        assert service.config == config
        assert service._node_cache == {}
    
    def test_create_hierarchy_node(self):
        """Test creating hierarchy node from task."""
        config = self.create_test_config()
        service = HierarchyService(config)
        task = self.create_test_task("task1")
        
        node = service.create_hierarchy_node(task)
        
        assert isinstance(node, HierarchyNode)
        assert node.task == task
    
    def test_build_hierarchy_tree(self):
        """Test building complete hierarchy tree."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        # Create tasks with hierarchy
        parent_task = self.create_test_task("parent", child_ids=["child1", "child2"])
        child1_task = self.create_test_task("child1", parent_id="parent")
        child2_task = self.create_test_task("child2", parent_id="parent")
        
        tasks = [parent_task, child1_task, child2_task]
        nodes = service.build_hierarchy_tree(tasks)
        
        assert len(nodes) == 3
        assert "parent" in nodes
        assert "child1" in nodes
        assert "child2" in nodes
        
        parent_node = nodes["parent"]
        child1_node = nodes["child1"]
        child2_node = nodes["child2"]
        
        assert len(parent_node.children) == 2
        assert child1_node in parent_node.children
        assert child2_node in parent_node.children
        assert child1_node.parent == parent_node
        assert child2_node.parent == parent_node
    
    def test_detect_cycles(self):
        """Test cycle detection in task hierarchy."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        # Create tasks with cycle: task1 -> task2 -> task1
        task1 = self.create_test_task("task1", parent_id="task2", child_ids=["task2"])
        task2 = self.create_test_task("task2", parent_id="task1", child_ids=["task1"])
        
        tasks = [task1, task2]
        cycles = service.detect_cycles(tasks)
        
        assert len(cycles) > 0
        assert "task1" in cycles or "task2" in cycles
    
    def test_validate_hierarchy_operation_valid(self):
        """Test validating valid hierarchy operation."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        parent_task = self.create_test_task("parent")
        child_task = self.create_test_task("child")
        
        tasks = [parent_task, child_task]
        
        assert service.validate_hierarchy_operation("parent", "child", tasks) is True
    
    def test_validate_hierarchy_operation_self_reference(self):
        """Test validating self-referencing hierarchy operation."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        task = self.create_test_task("task1")
        tasks = [task]
        
        assert service.validate_hierarchy_operation("task1", "task1", tasks) is False
    
    def test_validate_hierarchy_operation_would_create_cycle(self):
        """Test validating operation that would create cycle."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        # Create hierarchy: grandparent -> parent -> child
        grandparent_task = self.create_test_task("grandparent", child_ids=["parent"])
        parent_task = self.create_test_task("parent", parent_id="grandparent", child_ids=["child"])
        child_task = self.create_test_task("child", parent_id="parent")
        
        tasks = [grandparent_task, parent_task, child_task]
        
        # Try to make grandparent a child of child (would create cycle)
        assert service.validate_hierarchy_operation("child", "grandparent", tasks) is False
    
    def test_get_hierarchy_statistics(self):
        """Test getting hierarchy statistics."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        # Create hierarchy: root -> parent -> child1, child2
        root_task = self.create_test_task("root", child_ids=["parent"])
        parent_task = self.create_test_task("parent", parent_id="root", child_ids=["child1", "child2"])
        child1_task = self.create_test_task("child1", parent_id="parent")
        child2_task = self.create_test_task("child2", parent_id="parent")
        
        tasks = [root_task, parent_task, child1_task, child2_task]
        stats = service.get_hierarchy_statistics(tasks)
        
        assert stats["total_tasks"] == 4
        assert stats["root_tasks"] == 1
        assert stats["leaf_tasks"] == 2
        assert stats["max_depth"] == 2
        assert stats["avg_children"] == 0.75  # 3 total children / 4 tasks
        assert len(stats["cycles_detected"]) == 0
    
    def test_get_hierarchy_statistics_empty(self):
        """Test getting hierarchy statistics for empty task list."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        stats = service.get_hierarchy_statistics([])
        
        assert stats["total_tasks"] == 0
        assert stats["root_tasks"] == 0
        assert stats["leaf_tasks"] == 0
        assert stats["max_depth"] == 0
        assert stats["avg_children"] == 0.0
        assert len(stats["cycles_detected"]) == 0
    
    def test_get_task_path(self):
        """Test getting path from root to task."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        # Create hierarchy: root -> parent -> child
        root_task = self.create_test_task("root", child_ids=["parent"])
        parent_task = self.create_test_task("parent", parent_id="root", child_ids=["child"])
        child_task = self.create_test_task("child", parent_id="parent")
        
        tasks = [root_task, parent_task, child_task]
        path = service.get_task_path("child", tasks)
        
        assert path == ["root", "parent", "child"]
    
    def test_get_task_path_not_found(self):
        """Test getting path for non-existent task."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        task = self.create_test_task("task1")
        tasks = [task]
        path = service.get_task_path("nonexistent", tasks)
        
        assert path == []
    
    def test_get_subtree(self):
        """Test getting subtree from specific task."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        # Create hierarchy: root -> parent -> child
        root_task = self.create_test_task("root", child_ids=["parent"])
        parent_task = self.create_test_task("parent", parent_id="root", child_ids=["child"])
        child_task = self.create_test_task("child", parent_id="parent")
        
        tasks = [root_task, parent_task, child_task]
        subtree = service.get_subtree("parent", tasks)
        
        assert subtree["task"]["id"] == "parent"
        assert subtree["child_count"] == 1
        assert len(subtree["children"]) == 1
        assert subtree["children"][0]["task"]["id"] == "child"
    
    def test_get_subtree_not_found(self):
        """Test getting subtree for non-existent task."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        task = self.create_test_task("task1")
        tasks = [task]
        subtree = service.get_subtree("nonexistent", tasks)
        
        assert subtree == {}
    
    def test_get_subtree_max_depth(self):
        """Test getting subtree with max depth limit."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        # Create 3-level hierarchy
        root_task = self.create_test_task("root", child_ids=["parent"])
        parent_task = self.create_test_task("parent", parent_id="root", child_ids=["child"])
        child_task = self.create_test_task("child", parent_id="parent")
        
        tasks = [root_task, parent_task, child_task]
        subtree = service.get_subtree("root", tasks, max_depth=1)
        
        assert subtree["task"]["id"] == "root"
        assert len(subtree["children"]) == 1
        assert "children" not in subtree["children"][0]  # Should not include grandchildren
    
    def test_add_parent_child_relationship(self):
        """Test adding parent-child relationship."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        parent_task = self.create_test_task("parent")
        child_task = self.create_test_task("child")
        tasks = [parent_task, child_task]
        
        result = service.add_parent_child_relationship("parent", "child", tasks)
        
        assert result is True
        assert child_task.parent_id == "parent"
        assert "child" in parent_task.child_ids
    
    def test_add_parent_child_relationship_invalid(self):
        """Test adding invalid parent-child relationship."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        task = self.create_test_task("task1")
        tasks = [task]
        
        # Try to make task its own parent
        result = service.add_parent_child_relationship("task1", "task1", tasks)
        assert result is False
    
    def test_add_parent_child_relationship_moves_from_old_parent(self):
        """Test that adding relationship moves child from old parent."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        old_parent_task = self.create_test_task("old_parent", child_ids=["child"])
        new_parent_task = self.create_test_task("new_parent")
        child_task = self.create_test_task("child", parent_id="old_parent")
        tasks = [old_parent_task, new_parent_task, child_task]
        
        result = service.add_parent_child_relationship("new_parent", "child", tasks)
        
        assert result is True
        assert child_task.parent_id == "new_parent"
        assert "child" in new_parent_task.child_ids
        assert "child" not in old_parent_task.child_ids
    
    def test_remove_parent_child_relationship(self):
        """Test removing parent-child relationship."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        parent_task = self.create_test_task("parent", child_ids=["child"])
        child_task = self.create_test_task("child", parent_id="parent")
        tasks = [parent_task, child_task]
        
        result = service.remove_parent_child_relationship("parent", "child", tasks)
        
        assert result is True
        assert child_task.parent_id is None
        assert "child" not in parent_task.child_ids
    
    def test_remove_parent_child_relationship_not_found(self):
        """Test removing non-existent parent-child relationship."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        parent_task = self.create_test_task("parent")
        tasks = [parent_task]
        
        result = service.remove_parent_child_relationship("parent", "nonexistent", tasks)
        assert result is False
    
    def test_move_task_to_parent(self):
        """Test moving task to new parent."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        old_parent_task = self.create_test_task("old_parent", child_ids=["child"])
        new_parent_task = self.create_test_task("new_parent")
        child_task = self.create_test_task("child", parent_id="old_parent")
        tasks = [old_parent_task, new_parent_task, child_task]
        
        result = service.move_task_to_parent("child", "new_parent", tasks)
        
        assert result is True
        assert child_task.parent_id == "new_parent"
        assert "child" in new_parent_task.child_ids
        assert "child" not in old_parent_task.child_ids
    
    def test_move_task_to_root(self):
        """Test moving task to root level."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        parent_task = self.create_test_task("parent", child_ids=["child"])
        child_task = self.create_test_task("child", parent_id="parent")
        tasks = [parent_task, child_task]
        
        result = service.move_task_to_parent("child", None, tasks)
        
        assert result is True
        assert child_task.parent_id is None
        assert "child" not in parent_task.child_ids
    
    def test_move_task_would_create_cycle(self):
        """Test that moving task prevents cycles."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        # Create hierarchy: grandparent -> parent -> child
        grandparent_task = self.create_test_task("grandparent", child_ids=["parent"])
        parent_task = self.create_test_task("parent", parent_id="grandparent", child_ids=["child"])
        child_task = self.create_test_task("child", parent_id="parent")
        tasks = [grandparent_task, parent_task, child_task]
        
        # Try to move grandparent under child (would create cycle)
        result = service.move_task_to_parent("grandparent", "child", tasks)
        assert result is False
    
    def test_reassign_hierarchy(self):
        """Test batch hierarchy reassignment."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        # Create initial hierarchy
        root_task = self.create_test_task("root", child_ids=["child1", "child2"])
        new_parent_task = self.create_test_task("new_parent")
        child1_task = self.create_test_task("child1", parent_id="root")
        child2_task = self.create_test_task("child2", parent_id="root")
        tasks = [root_task, new_parent_task, child1_task, child2_task]
        
        # Move both children to new parent
        changes = [("child1", "new_parent"), ("child2", "new_parent")]
        result = service.reassign_hierarchy(changes, tasks)
        
        assert result is True
        assert child1_task.parent_id == "new_parent"
        assert child2_task.parent_id == "new_parent"
        assert "child1" in new_parent_task.child_ids
        assert "child2" in new_parent_task.child_ids
        assert len(root_task.child_ids) == 0
    
    def test_reassign_hierarchy_invalid_change(self):
        """Test batch hierarchy reassignment with invalid change."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        # Create hierarchy where moving would create cycle
        parent_task = self.create_test_task("parent", child_ids=["child"])
        child_task = self.create_test_task("child", parent_id="parent")
        tasks = [parent_task, child_task]
        
        # Try to move parent under child (would create cycle)
        changes = [("parent", "child")]
        result = service.reassign_hierarchy(changes, tasks)
        assert result is False
    
    def test_get_task_children(self):
        """Test getting direct children of a task."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        parent_task = self.create_test_task("parent", child_ids=["child1", "child2"])
        child1_task = self.create_test_task("child1", parent_id="parent")
        child2_task = self.create_test_task("child2", parent_id="parent")
        other_task = self.create_test_task("other")
        tasks = [parent_task, child1_task, child2_task, other_task]
        
        children = service.get_task_children("parent", tasks)
        
        assert len(children) == 2
        assert child1_task in children
        assert child2_task in children
        assert other_task not in children
    
    def test_get_task_children_not_found(self):
        """Test getting children of non-existent task."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        task = self.create_test_task("task1")
        tasks = [task]
        
        children = service.get_task_children("nonexistent", tasks)
        assert children == []
    
    def test_get_task_descendants_list(self):
        """Test getting all descendants of a task."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        # Create hierarchy: root -> parent -> child, grandchild
        root_task = self.create_test_task("root", child_ids=["parent"])
        parent_task = self.create_test_task("parent", parent_id="root", child_ids=["child"])
        child_task = self.create_test_task("child", parent_id="parent", child_ids=["grandchild"])
        grandchild_task = self.create_test_task("grandchild", parent_id="child")
        tasks = [root_task, parent_task, child_task, grandchild_task]
        
        descendants = service.get_task_descendants_list("root", tasks)
        
        assert len(descendants) == 3
        assert parent_task in descendants
        assert child_task in descendants
        assert grandchild_task in descendants
    
    def test_get_task_ancestors_list(self):
        """Test getting all ancestors of a task."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        # Create hierarchy: root -> parent -> child
        root_task = self.create_test_task("root", child_ids=["parent"])
        parent_task = self.create_test_task("parent", parent_id="root", child_ids=["child"])
        child_task = self.create_test_task("child", parent_id="parent")
        tasks = [root_task, parent_task, child_task]
        
        ancestors = service.get_task_ancestors_list("child", tasks)
        
        assert len(ancestors) == 2
        assert ancestors[0] == parent_task  # Immediate parent first
        assert ancestors[1] == root_task
    
    def test_ensure_hierarchy_consistency(self):
        """Test ensuring hierarchy consistency."""
        config = self.create_test_config()
        service = HierarchyService(config)
        
        # Create tasks with inconsistent relationships
        parent_task = self.create_test_task("parent", child_ids=["child1", "nonexistent"])
        child1_task = self.create_test_task("child1")  # Missing parent_id
        child2_task = self.create_test_task("child2", parent_id="nonexistent")  # Invalid parent
        tasks = [parent_task, child1_task, child2_task]
        
        issues_fixed = service.ensure_hierarchy_consistency(tasks)
        
        assert len(issues_fixed) > 0
        assert child1_task.parent_id == "parent"  # Should be fixed
        assert child2_task.parent_id is None  # Invalid parent should be removed
        assert "nonexistent" not in parent_task.child_ids  # Invalid child should be removed