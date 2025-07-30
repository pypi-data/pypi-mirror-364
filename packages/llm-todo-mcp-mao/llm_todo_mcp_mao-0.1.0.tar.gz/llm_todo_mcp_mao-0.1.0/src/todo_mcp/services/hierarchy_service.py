"""
Hierarchy management service for parent-child task relationships.

This module handles all operations related to task hierarchies,
including parent-child relationships, tree operations, and validation.
"""

import logging
from typing import Dict, List, Optional, Set, Any, ForwardRef
from pydantic import BaseModel, Field, field_validator, model_validator

from ..config import TodoConfig
from ..models.task import Task


class HierarchyNode(BaseModel):
    """
    Hierarchical node model for task tree structures.
    
    This model represents a node in the task hierarchy tree, containing
    a task and its relationships to parent and child nodes. Uses Pydantic's
    recursive model features for tree operations.
    """
    
    task: Task = Field(..., description="The task associated with this node")
    parent: Optional['HierarchyNode'] = Field(default=None, description="Parent node reference")
    children: List['HierarchyNode'] = Field(default_factory=list, description="Child node references")
    
    model_config = {
        "arbitrary_types_allowed": True,
    }
    
    @field_validator('children')
    @classmethod
    def validate_children(cls, v: List['HierarchyNode']) -> List['HierarchyNode']:
        """Validate children list and ensure no duplicates."""
        if not v:
            return []
        
        # Check for duplicate task IDs in children
        seen_ids = set()
        unique_children = []
        
        for child in v:
            if child.task.id not in seen_ids:
                seen_ids.add(child.task.id)
                unique_children.append(child)
        
        return unique_children
    
    @model_validator(mode='after')
    def validate_hierarchy_constraints(self) -> 'HierarchyNode':
        """Validate hierarchy constraints and prevent cycles."""
        # Ensure task ID consistency with parent/child relationships
        if self.parent and self.task.parent_id and self.task.parent_id != self.parent.task.id:
            raise ValueError(f"Task parent_id '{self.task.parent_id}' doesn't match parent node task ID '{self.parent.task.id}'")
        
        # Only validate child consistency if we have both task child_ids and children nodes
        if self.task.child_ids and self.children:
            child_ids_from_task = set(self.task.child_ids)
            child_ids_from_nodes = {child.task.id for child in self.children}
            
            if child_ids_from_task != child_ids_from_nodes:
                raise ValueError("Task child_ids don't match children node task IDs")
        
        # Prevent self-referencing
        if self.parent and self.parent.task.id == self.task.id:
            raise ValueError("Node cannot be its own parent")
        
        for child in self.children:
            if child.task.id == self.task.id:
                raise ValueError("Node cannot be its own child")
        
        return self
    
    def get_ancestors(self) -> List['HierarchyNode']:
        """
        Get all ancestor nodes from this node to the root.
        
        Returns:
            List of ancestor nodes, ordered from immediate parent to root
        """
        ancestors = []
        current = self.parent
        visited = {self.task.id}  # Track visited nodes to prevent infinite loops
        
        while current is not None:
            if current.task.id in visited:
                # Cycle detected, break to prevent infinite loop
                break
            
            ancestors.append(current)
            visited.add(current.task.id)
            current = current.parent
        
        return ancestors
    
    def get_descendants(self) -> List['HierarchyNode']:
        """
        Recursively get all descendant nodes.
        
        Returns:
            List of all descendant nodes in depth-first order
        """
        descendants = []
        visited = {self.task.id}  # Track visited nodes to prevent infinite loops
        
        def _collect_descendants(node: 'HierarchyNode') -> None:
            for child in node.children:
                if child.task.id not in visited:
                    visited.add(child.task.id)
                    descendants.append(child)
                    _collect_descendants(child)
        
        _collect_descendants(self)
        return descendants
    
    def get_root(self) -> 'HierarchyNode':
        """
        Get the root node of this hierarchy.
        
        Returns:
            The root node of the tree
        """
        current = self
        visited = {self.task.id}  # Track visited nodes to prevent infinite loops
        
        while current.parent is not None:
            if current.parent.task.id in visited:
                # Cycle detected, return current node
                break
            
            visited.add(current.parent.task.id)
            current = current.parent
        
        return current
    
    def get_depth(self) -> int:
        """
        Get the depth of this node in the hierarchy.
        
        Returns:
            Depth level (0 for root, 1 for first level children, etc.)
        """
        return len(self.get_ancestors())
    
    def get_sibling_nodes(self) -> List['HierarchyNode']:
        """
        Get all sibling nodes (nodes with the same parent).
        
        Returns:
            List of sibling nodes (excluding self)
        """
        if not self.parent:
            return []
        
        return [child for child in self.parent.children if child.task.id != self.task.id]
    
    def is_ancestor_of(self, other: 'HierarchyNode') -> bool:
        """
        Check if this node is an ancestor of another node.
        
        Args:
            other: Node to check
            
        Returns:
            True if this node is an ancestor of the other node
        """
        return self in other.get_ancestors()
    
    def is_descendant_of(self, other: 'HierarchyNode') -> bool:
        """
        Check if this node is a descendant of another node.
        
        Args:
            other: Node to check
            
        Returns:
            True if this node is a descendant of the other node
        """
        return other in self.get_ancestors()
    
    def validate_hierarchy(self) -> bool:
        """
        Validate the entire hierarchy for cycles and consistency.
        
        Returns:
            True if hierarchy is valid, False if cycles detected
        """
        try:
            # Check for cycles by traversing ancestors
            visited_ancestors = set()
            current = self
            
            while current is not None:
                if current.task.id in visited_ancestors:
                    return False  # Cycle detected in ancestors
                
                visited_ancestors.add(current.task.id)
                current = current.parent
            
            # Check for cycles in descendants
            visited_descendants = set()
            
            def _check_descendants(node: 'HierarchyNode') -> bool:
                if node.task.id in visited_descendants:
                    return False  # Cycle detected
                
                visited_descendants.add(node.task.id)
                
                for child in node.children:
                    if not _check_descendants(child):
                        return False
                
                visited_descendants.remove(node.task.id)
                return True
            
            return _check_descendants(self)
            
        except Exception:
            return False
    
    def validate_full_hierarchy(self) -> bool:
        """
        Validate the full hierarchy including task-node consistency.
        
        Returns:
            True if hierarchy is fully valid, False otherwise
        """
        try:
            # Check basic hierarchy validity
            if not self.validate_hierarchy():
                return False
            
            # Check task-node consistency
            if self.parent and self.task.parent_id != self.parent.task.id:
                return False
            
            if self.task.child_ids:
                child_ids_from_task = set(self.task.child_ids)
                child_ids_from_nodes = {child.task.id for child in self.children}
                
                if child_ids_from_task != child_ids_from_nodes:
                    return False
            
            # Recursively validate children
            for child in self.children:
                if not child.validate_full_hierarchy():
                    return False
            
            return True
            
        except Exception:
            return False
    
    def add_child_node(self, child_node: 'HierarchyNode') -> None:
        """
        Add a child node to this node.
        
        Args:
            child_node: Child node to add
            
        Raises:
            ValueError: If adding the child would create a cycle
        """
        # Check for cycles before adding
        if child_node.is_ancestor_of(self):
            raise ValueError(f"Cannot add child {child_node.task.id}: would create a cycle")
        
        # Check if child already exists
        if child_node.task.id in {child.task.id for child in self.children}:
            return  # Child already exists
        
        # Update relationships
        child_node.parent = self
        self.children.append(child_node)
        
        # Update task relationships
        self.task.add_child(child_node.task.id)
        child_node.task.parent_id = self.task.id
    
    def remove_child_node(self, child_id: str) -> bool:
        """
        Remove a child node by task ID.
        
        Args:
            child_id: ID of child task to remove
            
        Returns:
            True if child was removed, False if not found
        """
        for i, child in enumerate(self.children):
            if child.task.id == child_id:
                # Update relationships
                child.parent = None
                self.children.pop(i)
                
                # Update task relationships
                self.task.remove_child(child_id)
                child.task.parent_id = None
                
                return True
        
        return False
    
    def to_dict(self, include_children: bool = True, max_depth: Optional[int] = None) -> Dict[str, Any]:
        """
        Convert node to dictionary representation.
        
        Args:
            include_children: Whether to include children in output
            max_depth: Maximum depth to traverse (None for unlimited)
            
        Returns:
            Dictionary representation of the node
        """
        result = {
            "task": self.task.model_dump(),
            "depth": self.get_depth(),
            "has_parent": self.parent is not None,
            "child_count": len(self.children)
        }
        
        if include_children and (max_depth is None or max_depth > 0):
            next_depth = None if max_depth is None else max_depth - 1
            result["children"] = [
                child.to_dict(include_children=True, max_depth=next_depth)
                for child in self.children
            ]
        
        return result
    
    def __str__(self) -> str:
        """String representation of the hierarchy node."""
        return f"HierarchyNode({self.task.id}: {self.task.title})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"HierarchyNode(task_id='{self.task.id}', children={len(self.children)})"


# Enable forward references for recursive model
HierarchyNode.model_rebuild()


class HierarchyService:
    """
    Service for managing task hierarchies and parent-child relationships.
    
    This service provides operations for creating, modifying, and querying
    hierarchical task structures while maintaining data integrity.
    """
    
    def __init__(self, config: TodoConfig):
        """
        Initialize the hierarchy service.
        
        Args:
            config: Configuration settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._node_cache: Dict[str, HierarchyNode] = {}
    
    def create_hierarchy_node(self, task: Task) -> HierarchyNode:
        """
        Create a hierarchy node from a task.
        
        Args:
            task: Task to create node for
            
        Returns:
            HierarchyNode instance
        """
        return HierarchyNode(task=task)
    
    def build_hierarchy_tree(self, tasks: List[Task]) -> Dict[str, HierarchyNode]:
        """
        Build a complete hierarchy tree from a list of tasks.
        
        Args:
            tasks: List of tasks to build hierarchy from
            
        Returns:
            Dictionary mapping task IDs to HierarchyNode instances
        """
        # Create nodes for all tasks
        nodes = {task.id: HierarchyNode(task=task) for task in tasks}
        
        # Build parent-child relationships
        for task in tasks:
            node = nodes[task.id]
            
            # Set parent relationship
            if task.parent_id and task.parent_id in nodes:
                parent_node = nodes[task.parent_id]
                node.parent = parent_node
                
                # Add to parent's children if not already there
                if node not in parent_node.children:
                    parent_node.children.append(node)
            
            # Set child relationships
            for child_id in task.child_ids:
                if child_id in nodes:
                    child_node = nodes[child_id]
                    child_node.parent = node
                    
                    # Add to children if not already there
                    if child_node not in node.children:
                        node.children.append(child_node)
        
        # Validate all nodes for cycles
        for node in nodes.values():
            if not node.validate_hierarchy():
                self.logger.warning(f"Cycle detected in hierarchy for task {node.task.id}")
        
        return nodes
    
    def detect_cycles(self, tasks: List[Task]) -> List[str]:
        """
        Detect cycles in task hierarchy relationships.
        
        Args:
            tasks: List of tasks to check
            
        Returns:
            List of task IDs that are part of cycles
        """
        cycles = []
        task_map = {task.id: task for task in tasks}
        visited = set()
        rec_stack = set()
        
        def _has_cycle_dfs(task_id: str) -> bool:
            if task_id in rec_stack:
                return True  # Back edge found - cycle detected
            
            if task_id in visited:
                return False  # Already processed this node
            
            visited.add(task_id)
            rec_stack.add(task_id)
            
            task = task_map.get(task_id)
            if task:
                # Only check parent relationships to avoid double-checking
                if task.parent_id and _has_cycle_dfs(task.parent_id):
                    cycles.append(task_id)
                    rec_stack.remove(task_id)
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        # Check each unvisited task
        for task in tasks:
            if task.id not in visited:
                _has_cycle_dfs(task.id)
        
        return list(set(cycles))  # Remove duplicates
    
    def validate_hierarchy_operation(
        self, 
        parent_id: str, 
        child_id: str, 
        tasks: List[Task]
    ) -> bool:
        """
        Validate that adding a parent-child relationship won't create cycles.
        
        Args:
            parent_id: Parent task ID
            child_id: Child task ID
            tasks: Current list of tasks
            
        Returns:
            True if operation is valid, False if would create cycle
        """
        if parent_id == child_id:
            return False  # Self-referencing
        
        # Create a temporary task list with the new relationship
        task_map = {task.id: task for task in tasks}
        
        if parent_id not in task_map or child_id not in task_map:
            return False  # Tasks don't exist
        
        # Temporarily add the relationship
        parent_task = task_map[parent_id]
        child_task = task_map[child_id]
        
        # Check if child is already an ancestor of parent
        def _is_ancestor(ancestor_id: str, descendant_id: str, visited: Set[str]) -> bool:
            if ancestor_id == descendant_id:
                return True
            
            if descendant_id in visited:
                return False  # Prevent infinite loops
            
            visited.add(descendant_id)
            
            descendant_task = task_map.get(descendant_id)
            if descendant_task and descendant_task.parent_id:
                return _is_ancestor(ancestor_id, descendant_task.parent_id, visited)
            
            return False
        
        # Check if adding this relationship would create a cycle
        return not _is_ancestor(child_id, parent_id, set())
    
    def get_hierarchy_statistics(self, tasks: List[Task]) -> Dict[str, Any]:
        """
        Get statistics about the task hierarchy.
        
        Args:
            tasks: List of tasks to analyze
            
        Returns:
            Dictionary with hierarchy statistics
        """
        if not tasks:
            return {
                "total_tasks": 0,
                "root_tasks": 0,
                "leaf_tasks": 0,
                "max_depth": 0,
                "avg_children": 0.0,
                "cycles_detected": []
            }
        
        nodes = self.build_hierarchy_tree(tasks)
        
        root_tasks = [node for node in nodes.values() if node.parent is None]
        leaf_tasks = [node for node in nodes.values() if not node.children]
        
        # Calculate max depth
        max_depth = 0
        for node in nodes.values():
            depth = node.get_depth()
            max_depth = max(max_depth, depth)
        
        # Calculate average children per task
        total_children = sum(len(node.children) for node in nodes.values())
        avg_children = total_children / len(nodes) if nodes else 0.0
        
        # Detect cycles
        cycles = self.detect_cycles(tasks)
        
        return {
            "total_tasks": len(tasks),
            "root_tasks": len(root_tasks),
            "leaf_tasks": len(leaf_tasks),
            "max_depth": max_depth,
            "avg_children": round(avg_children, 2),
            "cycles_detected": cycles
        }
    
    def get_task_path(self, task_id: str, tasks: List[Task]) -> List[str]:
        """
        Get the path from root to a specific task.
        
        Args:
            task_id: Target task ID
            tasks: List of all tasks
            
        Returns:
            List of task IDs from root to target task
        """
        nodes = self.build_hierarchy_tree(tasks)
        
        if task_id not in nodes:
            return []
        
        node = nodes[task_id]
        ancestors = node.get_ancestors()
        
        # Build path from root to task
        path = [ancestor.task.id for ancestor in reversed(ancestors)]
        path.append(task_id)
        
        return path
    
    def get_subtree(self, root_task_id: str, tasks: List[Task], max_depth: Optional[int] = None) -> Dict[str, Any]:
        """
        Get a subtree starting from a specific task.
        
        Args:
            root_task_id: Root task ID for the subtree
            tasks: List of all tasks
            max_depth: Maximum depth to traverse
            
        Returns:
            Dictionary representation of the subtree
        """
        nodes = self.build_hierarchy_tree(tasks)
        
        if root_task_id not in nodes:
            return {}
        
        root_node = nodes[root_task_id]
        return root_node.to_dict(include_children=True, max_depth=max_depth)
    
    def add_parent_child_relationship(
        self, 
        parent_id: str, 
        child_id: str, 
        tasks: List[Task]
    ) -> bool:
        """
        Add a parent-child relationship between two tasks.
        
        Args:
            parent_id: Parent task ID
            child_id: Child task ID
            tasks: List of all tasks (will be modified in place)
            
        Returns:
            True if relationship was added successfully, False otherwise
        """
        if not self.validate_hierarchy_operation(parent_id, child_id, tasks):
            return False
        
        # Find the tasks
        parent_task = None
        child_task = None
        
        for task in tasks:
            if task.id == parent_id:
                parent_task = task
            elif task.id == child_id:
                child_task = task
        
        if not parent_task or not child_task:
            return False
        
        # Remove child from its current parent if it has one
        if child_task.parent_id:
            self.remove_parent_child_relationship(child_task.parent_id, child_id, tasks)
        
        # Add the new relationship
        parent_task.add_child(child_id)
        child_task.parent_id = parent_id
        
        return True
    
    def remove_parent_child_relationship(
        self, 
        parent_id: str, 
        child_id: str, 
        tasks: List[Task]
    ) -> bool:
        """
        Remove a parent-child relationship between two tasks.
        
        Args:
            parent_id: Parent task ID
            child_id: Child task ID
            tasks: List of all tasks (will be modified in place)
            
        Returns:
            True if relationship was removed successfully, False otherwise
        """
        # Find the tasks
        parent_task = None
        child_task = None
        
        for task in tasks:
            if task.id == parent_id:
                parent_task = task
            elif task.id == child_id:
                child_task = task
        
        if not parent_task or not child_task:
            return False
        
        # Remove the relationship
        parent_task.remove_child(child_id)
        if child_task.parent_id == parent_id:
            child_task.parent_id = None
        
        return True
    
    def move_task_to_parent(
        self, 
        task_id: str, 
        new_parent_id: Optional[str], 
        tasks: List[Task]
    ) -> bool:
        """
        Move a task to a new parent (or to root level if new_parent_id is None).
        
        Args:
            task_id: Task to move
            new_parent_id: New parent task ID (None for root level)
            tasks: List of all tasks (will be modified in place)
            
        Returns:
            True if task was moved successfully, False otherwise
        """
        # Find the task to move
        task_to_move = None
        for task in tasks:
            if task.id == task_id:
                task_to_move = task
                break
        
        if not task_to_move:
            return False
        
        # If moving to a parent, validate the operation
        if new_parent_id:
            if not self.validate_hierarchy_operation(new_parent_id, task_id, tasks):
                return False
        
        # Remove from current parent
        if task_to_move.parent_id:
            self.remove_parent_child_relationship(task_to_move.parent_id, task_id, tasks)
        
        # Add to new parent (or set to root)
        if new_parent_id:
            return self.add_parent_child_relationship(new_parent_id, task_id, tasks)
        else:
            # Moving to root level
            task_to_move.parent_id = None
            return True
    
    def reassign_hierarchy(
        self, 
        hierarchy_changes: List[tuple], 
        tasks: List[Task]
    ) -> bool:
        """
        Reassign multiple hierarchy relationships in a batch operation.
        
        Args:
            hierarchy_changes: List of tuples (child_id, new_parent_id)
                              where new_parent_id can be None for root level
            tasks: List of all tasks (will be modified in place)
            
        Returns:
            True if all changes were applied successfully, False otherwise
        """
        # Validate all changes first
        for child_id, new_parent_id in hierarchy_changes:
            if new_parent_id:
                if not self.validate_hierarchy_operation(new_parent_id, child_id, tasks):
                    return False
        
        # Apply all changes
        for child_id, new_parent_id in hierarchy_changes:
            if not self.move_task_to_parent(child_id, new_parent_id, tasks):
                return False
        
        return True
    
    def get_task_children(self, task_id: str, tasks: List[Task]) -> List[Task]:
        """
        Get all direct children of a task.
        
        Args:
            task_id: Parent task ID
            tasks: List of all tasks
            
        Returns:
            List of child tasks
        """
        parent_task = None
        for task in tasks:
            if task.id == task_id:
                parent_task = task
                break
        
        if not parent_task:
            return []
        
        children = []
        for task in tasks:
            if task.parent_id == task_id:
                children.append(task)
        
        return children
    
    def get_task_descendants_list(self, task_id: str, tasks: List[Task]) -> List[Task]:
        """
        Get all descendants of a task (children, grandchildren, etc.).
        
        Args:
            task_id: Root task ID
            tasks: List of all tasks
            
        Returns:
            List of descendant tasks
        """
        descendants = []
        task_map = {task.id: task for task in tasks}
        
        def _collect_descendants(current_id: str, visited: Set[str]) -> None:
            if current_id in visited:
                return  # Prevent infinite loops
            
            visited.add(current_id)
            current_task = task_map.get(current_id)
            
            if current_task:
                for child_id in current_task.child_ids:
                    if child_id in task_map:
                        descendants.append(task_map[child_id])
                        _collect_descendants(child_id, visited)
        
        _collect_descendants(task_id, set())
        return descendants
    
    def get_task_ancestors_list(self, task_id: str, tasks: List[Task]) -> List[Task]:
        """
        Get all ancestors of a task (parent, grandparent, etc.).
        
        Args:
            task_id: Child task ID
            tasks: List of all tasks
            
        Returns:
            List of ancestor tasks, ordered from immediate parent to root
        """
        ancestors = []
        task_map = {task.id: task for task in tasks}
        
        current_task = task_map.get(task_id)
        visited = {task_id}  # Prevent infinite loops
        
        while current_task and current_task.parent_id:
            if current_task.parent_id in visited:
                break  # Cycle detected
            
            parent_task = task_map.get(current_task.parent_id)
            if parent_task:
                ancestors.append(parent_task)
                visited.add(parent_task.id)
                current_task = parent_task
            else:
                break
        
        return ancestors
    
    def ensure_hierarchy_consistency(self, tasks: List[Task]) -> List[str]:
        """
        Ensure hierarchy consistency and fix any issues found.
        
        Args:
            tasks: List of all tasks (will be modified in place)
            
        Returns:
            List of issues that were fixed
        """
        issues_fixed = []
        task_map = {task.id: task for task in tasks}
        
        for task in tasks:
            # Fix parent-child consistency
            if task.parent_id:
                parent_task = task_map.get(task.parent_id)
                if parent_task:
                    # Ensure parent has this task in its children
                    if task.id not in parent_task.child_ids:
                        parent_task.add_child(task.id)
                        issues_fixed.append(f"Added {task.id} to parent {task.parent_id} children")
                else:
                    # Parent doesn't exist, remove parent reference
                    task.parent_id = None
                    issues_fixed.append(f"Removed invalid parent reference from {task.id}")
            
            # Fix child-parent consistency
            for child_id in task.child_ids[:]:  # Use slice to avoid modification during iteration
                child_task = task_map.get(child_id)
                if child_task:
                    # Ensure child has this task as parent
                    if child_task.parent_id != task.id:
                        child_task.parent_id = task.id
                        issues_fixed.append(f"Set parent of {child_id} to {task.id}")
                else:
                    # Child doesn't exist, remove from children
                    task.remove_child(child_id)
                    issues_fixed.append(f"Removed invalid child {child_id} from {task.id}")
        
        return issues_fixed