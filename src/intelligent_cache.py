#!/usr/bin/env python3
"""
Intelligent Cache System for Compliance Filter
Provides smart caching with TTL, LRU eviction, and content hashing
"""

import hashlib
import time
import threading
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, asdict
from collections import OrderedDict
import json
import logging
import os

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """A single cache entry with metadata"""
    data: Any
    timestamp: float
    access_count: int
    last_accessed: float
    content_hash: str
    ttl_seconds: Optional[int] = None

@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    max_size: int = 0
    hit_rate: float = 0.0
    
    def update_hit_rate(self):
        total = self.hits + self.misses
        self.hit_rate = (self.hits / total) if total > 0 else 0.0

class IntelligentCache:
    """
    Smart caching system with multiple eviction strategies and performance optimization
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600, 
                 enable_persistence: bool = True, cache_dir: str = "cache"):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.enable_persistence = enable_persistence
        self.cache_dir = cache_dir
        
        # Thread-safe cache storage
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = CacheStats(max_size=max_size)
        
        # Create cache directory if persistence is enabled
        if self.enable_persistence:
            os.makedirs(self.cache_dir, exist_ok=True)
            self._load_persistent_cache()
    
    def _generate_cache_key(self, text: str, context: Dict[str, Any] = None) -> str:
        """Generate a cache key from text and context"""
        # Create a hash of the text content
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
        
        # Include context if provided
        if context:
            context_str = json.dumps(context, sort_keys=True)
            context_hash = hashlib.sha256(context_str.encode('utf-8')).hexdigest()[:8]
            return f"{text_hash}_{context_hash}"
        
        return text_hash
    
    def _content_hash(self, data: Any) -> str:
        """Generate content hash for cache validation"""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()[:12]
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired"""
        if entry.ttl_seconds is None:
            return False
        return time.time() - entry.timestamp > entry.ttl_seconds
    
    def _evict_expired(self) -> int:
        """Remove expired entries and return count of evictions"""
        evicted_count = 0
        current_time = time.time()
        
        # Build list of expired keys to avoid modifying dict during iteration
        expired_keys = []
        for key, entry in self._cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        # Remove expired entries
        for key in expired_keys:
            del self._cache[key]
            evicted_count += 1
        
        return evicted_count
    
    def _evict_lru(self, count: int = 1) -> int:
        """Remove least recently used entries"""
        evicted_count = 0
        
        # Sort by last accessed time and remove oldest
        sorted_items = sorted(
            self._cache.items(), 
            key=lambda x: x[1].last_accessed
        )
        
        for i in range(min(count, len(sorted_items))):
            key = sorted_items[i][0]
            del self._cache[key]
            evicted_count += 1
        
        return evicted_count
    
    def _ensure_capacity(self) -> int:
        """Ensure cache doesn't exceed max size, return eviction count"""
        total_evicted = 0
        
        # First, remove expired entries
        total_evicted += self._evict_expired()
        
        # If still over capacity, use LRU eviction
        if len(self._cache) >= self.max_size:
            needed_space = len(self._cache) - self.max_size + 1
            total_evicted += self._evict_lru(needed_space)
        
        return total_evicted
    
    def get(self, text: str, context: Dict[str, Any] = None) -> Optional[Any]:
        """
        Get cached result for text and context
        
        Args:
            text: Text content to check
            context: Additional context for cache key
            
        Returns:
            Cached data if found and valid, None otherwise
        """
        cache_key = self._generate_cache_key(text, context)
        
        with self._lock:
            if cache_key not in self._cache:
                self._stats.misses += 1
                self._stats.update_hit_rate()
                return None
            
            entry = self._cache[cache_key]
            
            # Check if expired
            if self._is_expired(entry):
                del self._cache[cache_key]
                self._stats.misses += 1
                self._stats.evictions += 1
                self._stats.update_hit_rate()
                return None
            
            # Update access metadata
            entry.access_count += 1
            entry.last_accessed = time.time()
            
            # Move to end (most recently used)
            self._cache.move_to_end(cache_key)
            
            self._stats.hits += 1
            self._stats.update_hit_rate()
            
            logger.debug(f"Cache hit for key: {cache_key[:8]}...")
            return entry.data
    
    def put(self, text: str, data: Any, context: Dict[str, Any] = None, 
            ttl_seconds: Optional[int] = None) -> bool:
        """
        Store data in cache
        
        Args:
            text: Text content for cache key
            data: Data to cache
            context: Additional context for cache key
            ttl_seconds: Time to live in seconds, uses default if None
            
        Returns:
            True if successfully cached
        """
        cache_key = self._generate_cache_key(text, context)
        
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl
        
        with self._lock:
            # Ensure we have capacity
            evicted_count = self._ensure_capacity()
            self._stats.evictions += evicted_count
            
            # Create cache entry
            entry = CacheEntry(
                data=data,
                timestamp=time.time(),
                access_count=1,
                last_accessed=time.time(),
                content_hash=self._content_hash(data),
                ttl_seconds=ttl_seconds
            )
            
            self._cache[cache_key] = entry
            self._stats.size = len(self._cache)
            
            logger.debug(f"Cached result for key: {cache_key[:8]}...")
            
            # Persist to disk if enabled
            if self.enable_persistence:
                self._persist_entry(cache_key, entry)
            
            return True
    
    def invalidate(self, text: str, context: Dict[str, Any] = None) -> bool:
        """
        Remove specific entry from cache
        
        Args:
            text: Text content to invalidate
            context: Context used in original cache key
            
        Returns:
            True if entry was found and removed
        """
        cache_key = self._generate_cache_key(text, context)
        
        with self._lock:
            if cache_key in self._cache:
                del self._cache[cache_key]
                self._stats.size = len(self._cache)
                logger.debug(f"Invalidated cache key: {cache_key[:8]}...")
                return True
            return False
    
    def clear(self) -> int:
        """
        Clear all cache entries
        
        Returns:
            Number of entries cleared
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._stats = CacheStats(max_size=self.max_size)
            
            # Clear persistent cache
            if self.enable_persistence:
                self._clear_persistent_cache()
            
            logger.info(f"Cleared {count} cache entries")
            return count
    
    def cleanup(self) -> int:
        """
        Remove expired entries
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            evicted_count = self._evict_expired()
            self._stats.evictions += evicted_count
            self._stats.size = len(self._cache)
            
            if evicted_count > 0:
                logger.info(f"Cleaned up {evicted_count} expired cache entries")
            
            return evicted_count
    
    def get_stats(self) -> CacheStats:
        """Get current cache statistics"""
        with self._lock:
            stats = CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                evictions=self._stats.evictions,
                size=len(self._cache),
                max_size=self.max_size,
                hit_rate=self._stats.hit_rate
            )
            return stats
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information"""
        with self._lock:
            stats = self.get_stats()
            
            # Calculate additional metrics
            total_requests = stats.hits + stats.misses
            memory_usage = sum(len(str(entry.data)) for entry in self._cache.values())
            
            # Find most/least accessed entries
            if self._cache:
                access_counts = [entry.access_count for entry in self._cache.values()]
                most_accessed = max(access_counts)
                least_accessed = min(access_counts)
                avg_access = sum(access_counts) / len(access_counts)
            else:
                most_accessed = least_accessed = avg_access = 0
            
            return {
                'stats': asdict(stats),
                'total_requests': total_requests,
                'memory_usage_bytes': memory_usage,
                'avg_entry_size': memory_usage / len(self._cache) if self._cache else 0,
                'most_accessed_count': most_accessed,
                'least_accessed_count': least_accessed,
                'avg_access_count': avg_access,
                'oldest_entry_age': time.time() - min(
                    (entry.timestamp for entry in self._cache.values()), 
                    default=time.time()
                ),
                'cache_efficiency': stats.hit_rate * (stats.size / stats.max_size) if stats.max_size > 0 else 0
            }
    
    def _persist_entry(self, key: str, entry: CacheEntry):
        """Persist cache entry to disk"""
        if not self.enable_persistence:
            return
            
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            entry_data = {
                'data': entry.data,
                'timestamp': entry.timestamp,
                'access_count': entry.access_count,
                'last_accessed': entry.last_accessed,
                'content_hash': entry.content_hash,
                'ttl_seconds': entry.ttl_seconds
            }
            
            with open(cache_file, 'w') as f:
                json.dump(entry_data, f)
                
        except Exception as e:
            logger.warning(f"Failed to persist cache entry {key[:8]}: {e}")
    
    def _load_persistent_cache(self):
        """Load cache from persistent storage"""
        if not self.enable_persistence or not os.path.exists(self.cache_dir):
            return
        
        loaded_count = 0
        current_time = time.time()
        
        try:
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.json'):
                    continue
                    
                cache_key = filename[:-5]  # Remove .json extension
                cache_file = os.path.join(self.cache_dir, filename)
                
                try:
                    with open(cache_file, 'r') as f:
                        entry_data = json.load(f)
                    
                    entry = CacheEntry(**entry_data)
                    
                    # Skip expired entries
                    if self._is_expired(entry):
                        os.remove(cache_file)
                        continue
                    
                    self._cache[cache_key] = entry
                    loaded_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to load cache entry {cache_key[:8]}: {e}")
                    # Clean up corrupted cache file
                    try:
                        os.remove(cache_file)
                    except:
                        pass
        
            if loaded_count > 0:
                logger.info(f"Loaded {loaded_count} cache entries from persistence")
                
        except Exception as e:
            logger.warning(f"Failed to load persistent cache: {e}")
    
    def _clear_persistent_cache(self):
        """Clear persistent cache files"""
        if not self.enable_persistence or not os.path.exists(self.cache_dir):
            return
        
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
        except Exception as e:
            logger.warning(f"Failed to clear persistent cache: {e}")

# Singleton cache instance
_global_cache: Optional[IntelligentCache] = None

def get_cache() -> IntelligentCache:
    """Get or create global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = IntelligentCache()
    return _global_cache

def create_cache(max_size: int = 1000, default_ttl: int = 3600, 
                enable_persistence: bool = True) -> IntelligentCache:
    """Create a new cache instance with custom settings"""
    return IntelligentCache(
        max_size=max_size,
        default_ttl=default_ttl,
        enable_persistence=enable_persistence
    )

# Decorator for caching function results
def cached(ttl_seconds: Optional[int] = None, use_context: bool = False):
    """
    Decorator to cache function results
    
    Args:
        ttl_seconds: Time to live for cached results
        use_context: Whether to include function arguments in cache key
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Generate cache key from function name and arguments
            if use_context:
                context = {
                    'args': str(args[1:]),  # Skip 'self' if method
                    'kwargs': str(sorted(kwargs.items()))
                }
            else:
                context = None
            
            # Use first argument as text (assuming it's the content to analyze)
            text = str(args[1] if len(args) > 1 else args[0])
            cache_key = f"{func.__name__}_{text}"
            
            # Try to get from cache
            result = cache.get(cache_key, context)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.put(cache_key, result, context, ttl_seconds)
            
            return result
        return wrapper
    return decorator

if __name__ == "__main__":
    # Test the intelligent cache
    cache = IntelligentCache(max_size=5)
    
    print("🧠 Testing Intelligent Cache")
    print("=" * 40)
    
    # Test basic caching
    test_texts = [
        "This is a test message",
        "Another test message",
        "A third test message",
        "Fourth test message",
        "Fifth test message",
        "Sixth test message"  # This should trigger LRU eviction
    ]
    
    # Cache some results
    for i, text in enumerate(test_texts):
        cache.put(text, f"result_{i}", ttl_seconds=30)
        print(f"📝 Cached: {text[:20]}... -> result_{i}")
    
    print(f"\n📊 Cache Stats: {cache.get_stats()}")
    
    # Test retrieval
    print("\n🔍 Testing Retrieval:")
    for text in test_texts[:3]:
        result = cache.get(text)
        print(f"{'✅' if result else '❌'} {text[:20]}... -> {result}")
    
    # Test with context
    print("\n🎯 Testing Context-Aware Caching:")
    context1 = {"model": "gpt-4", "temperature": 0.7}
    context2 = {"model": "claude", "temperature": 0.5}
    
    cache.put("Hello world", "gpt4_result", context1)
    cache.put("Hello world", "claude_result", context2)
    
    result1 = cache.get("Hello world", context1)
    result2 = cache.get("Hello world", context2)
    
    print(f"✅ GPT-4 context: {result1}")
    print(f"✅ Claude context: {result2}")
    
    # Final stats
    print(f"\n📈 Final Stats: {cache.get_cache_info()}")
    
    # Test decorator
    print("\n🎨 Testing Decorator:")
    
    @cached(ttl_seconds=60, use_context=True)
    def dummy_analysis(text: str, model: str = "default") -> Dict[str, Any]:
        print(f"  🔧 Executing analysis for: {text[:20]}... with {model}")
        return {"result": f"analyzed_{text[:10]}", "model": model}
    
    # First call - should execute
    result = dummy_analysis("Test analysis text", model="gpt-4")
    print(f"  ✅ First call: {result}")
    
    # Second call - should use cache
    result = dummy_analysis("Test analysis text", model="gpt-4")
    print(f"  ⚡ Second call (cached): {result}")
    
    # Different context - should execute
    result = dummy_analysis("Test analysis text", model="claude")
    print(f"  ✅ Different context: {result}")