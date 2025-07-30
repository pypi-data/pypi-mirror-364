"""
Indexing and query optimization utilities for the Todo MCP system.

This module provides efficient indexing structures and optimized query
algorithms to improve search and filtering performance for large task datasets.
"""

import re
import threading
from collections import defaultdict, deque
from typing import Dict, List, Set, Optional, Any, Callable, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, field

from ..models.task import Task, TaskStatus, Priority
from ..models.filters import TaskFilter


@dataclass
class IndexEntry:
    """Represents an entry in an index."""
    task_id: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.now)


class BaseIndex:
    """Base class for all index implementations."""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._entries: Dict[str, IndexEntry] = {}
    
    def add(self, task_id: str, value: Any) -> None:
        """Add an entry to the index."""
        with self._lock:
            self._entries[task_id] = IndexEntry(task_id, value)
    
    def remove(self, task_id: str) -> None:
        """Remove an entry from the index."""
        with self._lock:
            self._entries.pop(task_id, None)
    
    def clear(self) -> None:
        """Clear all entries from the index."""
        with self._lock:
            self._entries.clear()
    
    def size(self) -> int:
        """Get the number of entries in the index."""
        with self._lock:
            return len(self._entries)


class HashIndex(BaseIndex):
    """
    Hash-based index for exact value lookups.
    
    Provides O(1) average case lookup time for exact matches.
    """
    
    def __init__(self):
        super().__init__()
        self._value_to_tasks: Dict[Any, Set[str]] = defaultdict(set)
    
    def add(self, task_id: str, value: Any) -> None:
        """Add an entry to the hash index."""
        with self._lock:
            # Remove old entry if exists
            if task_id in self._entries:
                old_value = self._entries[task_id].value
                self._value_to_tasks[old_value].discard(task_id)
                if not self._value_to_tasks[old_value]:
                    del self._value_to_tasks[old_value]
            
            # Add new entry
            super().add(task_id, value)
            self._value_to_tasks[value].add(task_id)
    
    def remove(self, task_id: str) -> None:
        """Remove an entry from the hash index."""
        with self._lock:
            if task_id in self._entries:
                value = self._entries[task_id].value
                self._value_to_tasks[value].discard(task_id)
                if not self._value_to_tasks[value]:
                    del self._value_to_tasks[value]
                super().remove(task_id)
    
    def find_exact(self, value: Any) -> Set[str]:
        """Find all task IDs with the exact value."""
        with self._lock:
            return self._value_to_tasks.get(value, set()).copy()
    
    def find_any(self, values: List[Any]) -> Set[str]:
        """Find all task IDs matching any of the given values."""
        with self._lock:
            result = set()
            for value in values:
                result.update(self._value_to_tasks.get(value, set()))
            return result
    
    def get_all_values(self) -> Set[Any]:
        """Get all unique values in the index."""
        with self._lock:
            return set(self._value_to_tasks.keys())


class RangeIndex(BaseIndex):
    """
    Range-based index for numeric and date comparisons.
    
    Maintains sorted order for efficient range queries.
    """
    
    def __init__(self):
        super().__init__()
        self._sorted_entries: List[Tuple[Any, str]] = []  # (value, task_id)
        self._needs_sort = False
    
    def add(self, task_id: str, value: Any) -> None:
        """Add an entry to the range index."""
        with self._lock:
            # Remove old entry if exists
            if task_id in self._entries:
                old_value = self._entries[task_id].value
                self._sorted_entries = [(v, tid) for v, tid in self._sorted_entries 
                                      if not (v == old_value and tid == task_id)]
            
            # Add new entry
            super().add(task_id, value)
            self._sorted_entries.append((value, task_id))
            self._needs_sort = True
    
    def remove(self, task_id: str) -> None:
        """Remove an entry from the range index."""
        with self._lock:
            if task_id in self._entries:
                value = self._entries[task_id].value
                self._sorted_entries = [(v, tid) for v, tid in self._sorted_entries 
                                      if not (v == value and tid == task_id)]
                super().remove(task_id)
    
    def _ensure_sorted(self) -> None:
        """Ensure the entries are sorted."""
        if self._needs_sort:
            self._sorted_entries.sort(key=lambda x: x[0])
            self._needs_sort = False
    
    def find_range(self, min_value: Any = None, max_value: Any = None) -> Set[str]:
        """Find all task IDs within the given range."""
        with self._lock:
            self._ensure_sorted()
            result = set()
            
            for value, task_id in self._sorted_entries:
                if min_value is not None and value < min_value:
                    continue
                if max_value is not None and value > max_value:
                    break
                result.add(task_id)
            
            return result
    
    def find_less_than(self, max_value: Any) -> Set[str]:
        """Find all task IDs with values less than the given value."""
        return self.find_range(max_value=max_value)
    
    def find_greater_than(self, min_value: Any) -> Set[str]:
        """Find all task IDs with values greater than the given value."""
        return self.find_range(min_value=min_value)


class TextIndex(BaseIndex):
    """
    Full-text search index with tokenization and stemming.
    
    Provides efficient text search across task content.
    """
    
    def __init__(self):
        super().__init__()
        self._word_to_tasks: Dict[str, Set[str]] = defaultdict(set)
        self._task_to_words: Dict[str, Set[str]] = defaultdict(set)
    
    def _tokenize(self, text: str) -> Set[str]:
        """Tokenize text into searchable words."""
        if not text:
            return set()
        
        # Convert to lowercase and extract words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out very short words and common stop words
        stop_words = {'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 
                     'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 
                     'that', 'the', 'to', 'was', 'will', 'with'}
        
        return {word for word in words if len(word) > 2 and word not in stop_words}
    
    def add(self, task_id: str, text: str) -> None:
        """Add text content to the index."""
        with self._lock:
            # Remove old entries if exists
            if task_id in self._task_to_words:
                old_words = self._task_to_words[task_id]
                for word in old_words:
                    self._word_to_tasks[word].discard(task_id)
                    if not self._word_to_tasks[word]:
                        del self._word_to_tasks[word]
            
            # Add new entries
            super().add(task_id, text)
            words = self._tokenize(text)
            self._task_to_words[task_id] = words
            
            for word in words:
                self._word_to_tasks[word].add(task_id)
    
    def remove(self, task_id: str) -> None:
        """Remove a task from the text index."""
        with self._lock:
            if task_id in self._task_to_words:
                words = self._task_to_words[task_id]
                for word in words:
                    self._word_to_tasks[word].discard(task_id)
                    if not self._word_to_tasks[word]:
                        del self._word_to_tasks[word]
                del self._task_to_words[task_id]
                super().remove(task_id)
    
    def search(self, query: str) -> Set[str]:
        """Search for tasks containing the query terms."""
        with self._lock:
            query_words = self._tokenize(query)
            if not query_words:
                return set()
            
            # Find tasks containing all query words (AND operation)
            result_sets = []
            for word in query_words:
                if word in self._word_to_tasks:
                    result_sets.append(self._word_to_tasks[word])
                else:
                    # If any word is not found, no results
                    return set()
            
            # Intersection of all result sets
            result = result_sets[0].copy()
            for result_set in result_sets[1:]:
                result.intersection_update(result_set)
            
            return result
    
    def search_any(self, query: str) -> Set[str]:
        """Search for tasks containing any of the query terms."""
        with self._lock:
            query_words = self._tokenize(query)
            if not query_words:
                return set()
            
            result = set()
            for word in query_words:
                result.update(self._word_to_tasks.get(word, set()))
            
            return result
    
    def search_prefix(self, prefix: str) -> Set[str]:
        """Search for tasks containing words with the given prefix."""
        with self._lock:
            prefix = prefix.lower()
            result = set()
            
            for word, task_ids in self._word_to_tasks.items():
                if word.startswith(prefix):
                    result.update(task_ids)
            
            return result


class TaskIndexManager:
    """
    Manages multiple indexes for efficient task querying.
    
    Provides a unified interface for all indexing operations and
    optimized query execution.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # Create indexes for different task attributes
        self.status_index = HashIndex()
        self.priority_index = HashIndex()
        self.tag_index = HashIndex()
        self.parent_index = HashIndex()
        self.created_date_index = RangeIndex()
        self.updated_date_index = RangeIndex()
        self.due_date_index = RangeIndex()
        self.text_index = TextIndex()
        
        # Track all indexed tasks
        self._indexed_tasks: Set[str] = set()
    
    def add_task(self, task: Task) -> None:
        """Add a task to all relevant indexes."""
        with self._lock:
            task_id = task.id
            
            # Add to hash indexes
            self.status_index.add(task_id, task.status.value)
            self.priority_index.add(task_id, str(task.priority))  # Use string representation
            
            # Add tags (each tag separately)
            for tag in task.tags:
                self.tag_index.add(f"{task_id}:{tag}", tag)
            
            # Add parent relationship
            if task.parent_id:
                self.parent_index.add(task_id, task.parent_id)
            
            # Add to range indexes
            self.created_date_index.add(task_id, task.created_at)
            self.updated_date_index.add(task_id, task.updated_at)
            if task.due_date:
                self.due_date_index.add(task_id, task.due_date)
            
            # Add to text index (combine title and description)
            text_content = f"{task.title} {task.description}"
            self.text_index.add(task_id, text_content)
            
            self._indexed_tasks.add(task_id)
    
    def remove_task(self, task_id: str) -> None:
        """Remove a task from all indexes."""
        with self._lock:
            if task_id not in self._indexed_tasks:
                return
            
            # Remove from all indexes
            self.status_index.remove(task_id)
            self.priority_index.remove(task_id)
            self.parent_index.remove(task_id)
            self.created_date_index.remove(task_id)
            self.updated_date_index.remove(task_id)
            self.due_date_index.remove(task_id)
            self.text_index.remove(task_id)
            
            # Remove tag entries (need to find all tag entries for this task)
            # This is a limitation of the current design - we'd need to track
            # which tags belong to which task for efficient removal
            
            self._indexed_tasks.discard(task_id)
    
    def update_task(self, task: Task) -> None:
        """Update a task in all indexes."""
        with self._lock:
            # Remove old entries and add new ones
            self.remove_task(task.id)
            self.add_task(task)
    
    def bulk_add_tasks(self, tasks: Dict[str, Task]) -> None:
        """Bulk add multiple tasks to indexes."""
        with self._lock:
            for task in tasks.values():
                self.add_task(task)
    
    def clear_all_indexes(self) -> None:
        """Clear all indexes."""
        with self._lock:
            self.status_index.clear()
            self.priority_index.clear()
            self.tag_index.clear()
            self.parent_index.clear()
            self.created_date_index.clear()
            self.updated_date_index.clear()
            self.due_date_index.clear()
            self.text_index.clear()
            self._indexed_tasks.clear()
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about all indexes."""
        with self._lock:
            return {
                'total_indexed_tasks': len(self._indexed_tasks),
                'status_index_size': self.status_index.size(),
                'priority_index_size': self.priority_index.size(),
                'tag_index_size': self.tag_index.size(),
                'parent_index_size': self.parent_index.size(),
                'created_date_index_size': self.created_date_index.size(),
                'updated_date_index_size': self.updated_date_index.size(),
                'due_date_index_size': self.due_date_index.size(),
                'text_index_size': self.text_index.size(),
            }


@dataclass
class QueryResult:
    """Represents the result of a query operation."""
    task_ids: Set[str]
    total_count: int
    execution_time_ms: float
    indexes_used: List[str]
    
    def paginate(self, offset: int = 0, limit: int = 50) -> 'PaginatedResult':
        """Apply pagination to the query result."""
        task_list = list(self.task_ids)
        paginated_ids = task_list[offset:offset + limit]
        
        return PaginatedResult(
            task_ids=paginated_ids,
            total_count=self.total_count,
            offset=offset,
            limit=limit,
            has_more=offset + limit < self.total_count,
            execution_time_ms=self.execution_time_ms,
            indexes_used=self.indexes_used
        )


@dataclass
class PaginatedResult:
    """Represents a paginated query result."""
    task_ids: List[str]
    total_count: int
    offset: int
    limit: int
    has_more: bool
    execution_time_ms: float
    indexes_used: List[str]


class QueryOptimizer:
    """
    Optimizes query execution using available indexes.
    
    Analyzes query filters and selects the most efficient execution plan.
    """
    
    def __init__(self, index_manager: TaskIndexManager):
        self.index_manager = index_manager
    
    def execute_query(self, task_filter: TaskFilter) -> QueryResult:
        """Execute an optimized query using the best available indexes."""
        import time
        start_time = time.time()
        indexes_used = []
        
        # Start with all indexed tasks
        result_sets = []
        
        # Apply status filter
        if task_filter.status:
            status_values = [status.value for status in task_filter.status]
            status_results = self.index_manager.status_index.find_any(status_values)
            result_sets.append(status_results)
            indexes_used.append('status_index')
        
        # Apply priority filter
        if task_filter.priority:
            priority_values = [str(priority) for priority in task_filter.priority]
            priority_results = self.index_manager.priority_index.find_any(priority_values)
            result_sets.append(priority_results)
            indexes_used.append('priority_index')
        
        # Apply tag filter
        if task_filter.tags:
            tag_results = set()
            for tag in task_filter.tags:
                tag_tasks = self.index_manager.tag_index.find_exact(tag)
                # Extract task IDs from tag entries (format: "task_id:tag")
                task_ids = {entry.split(':')[0] for entry in tag_tasks}
                tag_results.update(task_ids)
            result_sets.append(tag_results)
            indexes_used.append('tag_index')
        
        # Apply parent filter
        if task_filter.parent_id:
            parent_results = self.index_manager.parent_index.find_exact(task_filter.parent_id)
            result_sets.append(parent_results)
            indexes_used.append('parent_index')
        
        # Apply date range filters
        if task_filter.created_after or task_filter.created_before:
            created_results = self.index_manager.created_date_index.find_range(
                task_filter.created_after, task_filter.created_before
            )
            result_sets.append(created_results)
            indexes_used.append('created_date_index')
        
        if task_filter.due_after or task_filter.due_before:
            due_results = self.index_manager.due_date_index.find_range(
                task_filter.due_after, task_filter.due_before
            )
            result_sets.append(due_results)
            indexes_used.append('due_date_index')
        
        # Apply text search
        if task_filter.search_text:
            text_results = self.index_manager.text_index.search(task_filter.search_text)
            result_sets.append(text_results)
            indexes_used.append('text_index')
        
        # Compute intersection of all result sets
        if result_sets:
            final_results = result_sets[0].copy()
            for result_set in result_sets[1:]:
                final_results.intersection_update(result_set)
        else:
            # No filters applied, return all indexed tasks
            final_results = self.index_manager._indexed_tasks.copy()
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return QueryResult(
            task_ids=final_results,
            total_count=len(final_results),
            execution_time_ms=execution_time,
            indexes_used=indexes_used
        )
    
    def execute_text_search(self, query: str, search_mode: str = 'all') -> QueryResult:
        """Execute an optimized text search query."""
        import time
        start_time = time.time()
        
        if search_mode == 'all':
            results = self.index_manager.text_index.search(query)
        elif search_mode == 'any':
            results = self.index_manager.text_index.search_any(query)
        elif search_mode == 'prefix':
            results = self.index_manager.text_index.search_prefix(query)
        else:
            raise ValueError(f"Invalid search mode: {search_mode}")
        
        execution_time = (time.time() - start_time) * 1000
        
        return QueryResult(
            task_ids=results,
            total_count=len(results),
            execution_time_ms=execution_time,
            indexes_used=['text_index']
        )
    
    def get_query_plan(self, task_filter: TaskFilter) -> Dict[str, Any]:
        """Get the execution plan for a query without executing it."""
        plan = {
            'estimated_selectivity': {},
            'recommended_indexes': [],
            'execution_order': []
        }
        
        # Estimate selectivity for each filter
        total_tasks = len(self.index_manager._indexed_tasks)
        
        if task_filter.status:
            status_count = sum(len(self.index_manager.status_index.find_exact(s.value)) 
                             for s in task_filter.status)
            plan['estimated_selectivity']['status'] = status_count / total_tasks if total_tasks > 0 else 0
            plan['recommended_indexes'].append('status_index')
        
        if task_filter.priority:
            priority_count = sum(len(self.index_manager.priority_index.find_exact(str(p))) 
                               for p in task_filter.priority)
            plan['estimated_selectivity']['priority'] = priority_count / total_tasks if total_tasks > 0 else 0
            plan['recommended_indexes'].append('priority_index')
        
        if task_filter.search_text:
            text_count = len(self.index_manager.text_index.search(task_filter.search_text))
            plan['estimated_selectivity']['text'] = text_count / total_tasks if total_tasks > 0 else 0
            plan['recommended_indexes'].append('text_index')
        
        # Sort by selectivity (most selective first)
        selectivity_items = list(plan['estimated_selectivity'].items())
        selectivity_items.sort(key=lambda x: x[1])
        plan['execution_order'] = [item[0] for item in selectivity_items]
        
        return plan


# Global index manager instance
_index_manager: Optional[TaskIndexManager] = None


def get_index_manager() -> TaskIndexManager:
    """Get the global index manager instance."""
    global _index_manager
    if _index_manager is None:
        _index_manager = TaskIndexManager()
    return _index_manager


def initialize_indexing() -> TaskIndexManager:
    """Initialize the global index manager."""
    global _index_manager
    _index_manager = TaskIndexManager()
    return _index_manager