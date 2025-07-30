"""
Memory caching utilities with LRU eviction and persistence support.

This module provides a comprehensive caching system for the Todo MCP server
to improve performance by reducing file I/O operations and speeding up
frequently accessed data.
"""

import json
import pickle
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, Optional, Set, TypeVar, Generic, Callable
from datetime import datetime, timedelta

from ..models.task import Task

T = TypeVar('T')


class CacheEntry(Generic[T]):
    """Represents a single cache entry with metadata."""
    
    def __init__(self, value: T, ttl: Optional[float] = None):
        self.value = value
        self.created_at = time.time()
        self.last_accessed = self.created_at
        self.access_count = 1
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def touch(self) -> None:
        """Update access metadata."""
        self.last_accessed = time.time()
        self.access_count += 1


class LRUCache(Generic[T]):
    """
    Thread-safe LRU (Least Recently Used) cache implementation.
    
    Features:
    - LRU eviction policy
    - TTL (Time To Live) support
    - Thread-safe operations
    - Cache statistics
    - Persistence support
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry[T]] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired': 0
        }
    
    def get(self, key: str) -> Optional[T]:
        """Get a value from the cache."""
        with self._lock:
            if key not in self._cache:
                self._stats['misses'] += 1
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self._cache[key]
                self._stats['expired'] += 1
                self._stats['misses'] += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()
            self._stats['hits'] += 1
            return entry.value
    
    def put(self, key: str, value: T, ttl: Optional[float] = None) -> None:
        """Put a value into the cache."""
        with self._lock:
            # Use default TTL if not specified
            if ttl is None:
                ttl = self.default_ttl
            
            # If key exists, update it
            if key in self._cache:
                self._cache[key] = CacheEntry(value, ttl)
                self._cache.move_to_end(key)
                return
            
            # Add new entry
            self._cache[key] = CacheEntry(value, ttl)
            
            # Evict if necessary
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._stats['evictions'] += 1
    
    def delete(self, key: str) -> bool:
        """Delete a key from the cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """Get the current cache size."""
        with self._lock:
            return len(self._cache)
    
    def keys(self) -> Set[str]:
        """Get all cache keys."""
        with self._lock:
            return set(self._cache.keys())
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed items."""
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                self._stats['expired'] += 1
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate': hit_rate,
                'evictions': self._stats['evictions'],
                'expired': self._stats['expired']
            }


class TaskCache:
    """
    Specialized cache for Task objects with additional features.
    
    Features:
    - Task-specific caching logic
    - Dependency tracking
    - Bulk operations
    - Persistence support
    """
    
    def __init__(self, max_size: int = 1000, ttl: float = 3600):  # 1 hour TTL
        self._task_cache = LRUCache[Task](max_size, ttl)
        self._hierarchy_cache = LRUCache[Dict[str, Any]](max_size // 4, ttl)
        self._query_cache = LRUCache[Dict[str, Any]](max_size // 2, ttl * 0.5)  # Shorter TTL for queries
        self._dependency_map: Dict[str, Set[str]] = {}
        self._lock = threading.RLock()
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task from the cache."""
        return self._task_cache.get(task_id)
    
    def put_task(self, task: Task) -> None:
        """Put a task into the cache."""
        with self._lock:
            self._task_cache.put(task.id, task)
            self._update_dependencies(task)
    
    def delete_task(self, task_id: str) -> None:
        """Delete a task from the cache and invalidate related entries."""
        with self._lock:
            self._task_cache.delete(task_id)
            self._invalidate_dependencies(task_id)
    
    def get_hierarchy(self, root_id: str) -> Optional[Dict[str, Any]]:
        """Get cached hierarchy data."""
        return self._hierarchy_cache.get(f"hierarchy_{root_id}")
    
    def put_hierarchy(self, root_id: str, hierarchy_data: Dict[str, Any]) -> None:
        """Cache hierarchy data."""
        self._hierarchy_cache.put(f"hierarchy_{root_id}", hierarchy_data)
    
    def get_query_result(self, query_key: str) -> Optional[Dict[str, Any]]:
        """Get cached query result."""
        return self._query_cache.get(query_key)
    
    def put_query_result(self, query_key: str, result: Dict[str, Any]) -> None:
        """Cache query result."""
        self._query_cache.put(query_key, result)
    
    def invalidate_queries(self) -> None:
        """Invalidate all cached query results."""
        self._query_cache.clear()
    
    def _update_dependencies(self, task: Task) -> None:
        """Update dependency tracking for a task."""
        task_id = task.id
        dependencies = set()
        
        # Add parent dependency
        if task.parent_id:
            dependencies.add(task.parent_id)
        
        # Add child dependencies
        dependencies.update(task.child_ids)
        
        self._dependency_map[task_id] = dependencies
    
    def _invalidate_dependencies(self, task_id: str) -> None:
        """Invalidate cache entries that depend on the given task."""
        # Invalidate hierarchy cache for this task itself
        self._hierarchy_cache.delete(f"hierarchy_{task_id}")
        
        # Invalidate hierarchy cache for its dependencies
        if task_id in self._dependency_map:
            for dep_id in self._dependency_map[task_id]:
                self._hierarchy_cache.delete(f"hierarchy_{dep_id}")
        
        # Remove from dependency map
        self._dependency_map.pop(task_id, None)
        
        # Invalidate all query results since task relationships changed
        self.invalidate_queries()
    
    def bulk_put_tasks(self, tasks: Dict[str, Task]) -> None:
        """Bulk insert tasks into cache."""
        with self._lock:
            for task_id, task in tasks.items():
                self._task_cache.put(task_id, task)
                self._update_dependencies(task)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        return {
            'task_cache': self._task_cache.get_stats(),
            'hierarchy_cache': self._hierarchy_cache.get_stats(),
            'query_cache': self._query_cache.get_stats(),
            'dependencies_tracked': len(self._dependency_map)
        }
    
    def cleanup(self) -> Dict[str, int]:
        """Clean up expired entries from all caches."""
        return {
            'task_expired': self._task_cache.cleanup_expired(),
            'hierarchy_expired': self._hierarchy_cache.cleanup_expired(),
            'query_expired': self._query_cache.cleanup_expired()
        }


class CacheManager:
    """
    Global cache manager for the Todo MCP system.
    
    Provides centralized cache management with persistence and prewarming.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.cwd() / "data" / "cache"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.task_cache = TaskCache()
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()
        self._persistence_enabled = True
    
    def enable_persistence(self, enabled: bool = True) -> None:
        """Enable or disable cache persistence."""
        self._persistence_enabled = enabled
    
    def save_to_disk(self) -> None:
        """Persist cache data to disk."""
        if not self._persistence_enabled:
            return
        
        try:
            cache_file = self.config_dir / "task_cache.pkl"
            with open(cache_file, 'wb') as f:
                # Save only the task cache data, not the entire cache objects
                cache_data = {}
                for key in self.task_cache._task_cache.keys():
                    task = self.task_cache._task_cache.get(key)
                    if task:
                        cache_data[key] = task
                
                pickle.dump(cache_data, f)
        except Exception as e:
            # Log error but don't fail the application
            print(f"Warning: Failed to persist cache: {e}")
    
    def load_from_disk(self) -> int:
        """Load cache data from disk."""
        if not self._persistence_enabled:
            return 0
        
        try:
            cache_file = self.config_dir / "task_cache.pkl"
            if not cache_file.exists():
                return 0
            
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                self.task_cache.bulk_put_tasks(cache_data)
                return len(cache_data)
        except Exception as e:
            print(f"Warning: Failed to load cache: {e}")
            return 0
    
    def prewarm_cache(self, task_loader: Callable[[], Dict[str, Task]]) -> int:
        """Prewarm the cache with frequently accessed tasks."""
        try:
            tasks = task_loader()
            self.task_cache.bulk_put_tasks(tasks)
            return len(tasks)
        except Exception as e:
            print(f"Warning: Failed to prewarm cache: {e}")
            return 0
    
    def periodic_cleanup(self) -> None:
        """Perform periodic cleanup if needed."""
        current_time = time.time()
        if current_time - self._last_cleanup > self._cleanup_interval:
            self.task_cache.cleanup()
            self._last_cleanup = current_time
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all caches."""
        stats = self.task_cache.get_stats()
        stats['persistence_enabled'] = self._persistence_enabled
        stats['last_cleanup'] = self._last_cleanup
        return stats
    
    def clear_all_caches(self) -> None:
        """Clear all caches."""
        self.task_cache._task_cache.clear()
        self.task_cache._hierarchy_cache.clear()
        self.task_cache._query_cache.clear()
        self.task_cache._dependency_map.clear()


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def initialize_cache(config_dir: Optional[Path] = None) -> CacheManager:
    """Initialize the global cache manager."""
    global _cache_manager
    _cache_manager = CacheManager(config_dir)
    return _cache_manager