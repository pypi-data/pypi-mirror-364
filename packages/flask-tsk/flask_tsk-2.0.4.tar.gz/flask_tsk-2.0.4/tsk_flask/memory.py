#!/usr/bin/env python3
"""
TuskFlask Memory Management Module
Provides memory management and caching functionality for elephant services
"""

import time
import threading
from typing import Any, Dict, Optional, List
from collections import OrderedDict


class Memory:
    """Simple in-memory storage with TTL support"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache = OrderedDict()
        self._lock = threading.RLock()
        self._cleanup_thread = None
        self._stop_cleanup = False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from memory cache"""
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if expiry is None or time.time() < expiry:
                    # Move to end (LRU)
                    self._cache.move_to_end(key)
                    return value
                else:
                    # Expired, remove it
                    del self._cache[key]
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in memory cache with optional TTL"""
        with self._lock:
            if ttl is None:
                ttl = self.default_ttl
            
            expiry = time.time() + ttl if ttl > 0 else None
            
            # Remove if exists
            if key in self._cache:
                del self._cache[key]
            
            # Add new entry
            self._cache[key] = (value, expiry)
            
            # Enforce max size
            if len(self._cache) > self.max_size:
                self._cache.popitem(last=False)
            
            return True
    
    def delete(self, key: str) -> bool:
        """Delete key from memory cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        return self.get(key) is not None
    
    def clear(self) -> None:
        """Clear all cached data"""
        with self._lock:
            self._cache.clear()
    
    def keys(self) -> List[str]:
        """Get all valid keys"""
        with self._lock:
            valid_keys = []
            current_time = time.time()
            for key, (value, expiry) in self._cache.items():
                if expiry is None or current_time < expiry:
                    valid_keys.append(key)
            return valid_keys
    
    def size(self) -> int:
        """Get current cache size"""
        with self._lock:
            return len(self._cache)
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed items"""
        with self._lock:
            current_time = time.time()
            expired_keys = []
            
            for key, (value, expiry) in self._cache.items():
                if expiry is not None and current_time >= expiry:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            current_time = time.time()
            total_items = len(self._cache)
            expired_items = 0
            valid_items = 0
            
            for value, expiry in self._cache.values():
                if expiry is None or current_time < expiry:
                    valid_items += 1
                else:
                    expired_items += 1
            
            return {
                'total_items': total_items,
                'valid_items': valid_items,
                'expired_items': expired_items,
                'max_size': self.max_size,
                'default_ttl': self.default_ttl
            }


# Global memory instance
_memory_instance = None


def get_memory() -> Memory:
    """Get global memory instance"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = Memory()
    return _memory_instance


def init_memory(max_size: int = 1000, default_ttl: int = 3600) -> Memory:
    """Initialize global memory instance"""
    global _memory_instance
    _memory_instance = Memory(max_size, default_ttl)
    return _memory_instance 