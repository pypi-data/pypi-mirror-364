"""Caching system for ACE IoT models."""

import hashlib
import json
import time
from collections import OrderedDict
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from .config import get_config


T = TypeVar("T")


class CacheStats:
    """Track cache statistics."""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.total_requests = 0
        self.start_time = time.time()

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "total_requests": self.total_requests,
            "hit_rate": self.hit_rate,
            "uptime_seconds": time.time() - self.start_time,
        }


class LRUCache:
    """Least Recently Used (LRU) cache implementation."""

    def __init__(self, max_size: int | None = None, default_ttl: int | None = None):
        config = get_config()
        self.max_size = max_size or config.cache.max_cache_size
        self.default_ttl = default_ttl or config.cache.default_ttl
        self.cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self.stats = CacheStats() if config.cache.enable_cache_stats else None

    def _is_expired(self, timestamp: float) -> bool:
        """Check if cache entry is expired."""
        if self.default_ttl <= 0:
            return False
        return time.time() - timestamp > self.default_ttl

    def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if self.stats:
            self.stats.total_requests += 1

        if key not in self.cache:
            if self.stats:
                self.stats.misses += 1
            return None

        value, timestamp = self.cache[key]

        # Check expiration
        if self._is_expired(timestamp):
            del self.cache[key]
            if self.stats:
                self.stats.misses += 1
            return None

        # Move to end (most recently used)
        self.cache.move_to_end(key)

        if self.stats:
            self.stats.hits += 1

        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache."""
        # Note: ttl parameter kept for API compatibility but not used in this implementation
        _ = ttl  # Mark as intentionally unused
        # Remove if already exists to update position
        if key in self.cache:
            del self.cache[key]

        # Add to end
        self.cache[key] = (value, time.time())

        # Evict oldest if over capacity
        while len(self.cache) > self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            if self.stats:
                self.stats.evictions += 1

    def invalidate(self, key: str) -> bool:
        """Remove key from cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def invalidate_prefix(self, prefix: str) -> int:
        """Remove all keys with given prefix."""
        keys_to_remove = [k for k in self.cache if k.startswith(prefix)]
        for key in keys_to_remove:
            del self.cache[key]
        return len(keys_to_remove)

    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()

    def get_stats(self) -> dict[str, Any] | None:
        """Get cache statistics."""
        return self.stats.to_dict() if self.stats else None


class ModelCache:
    """Cache specifically for model operations."""

    def __init__(self):
        self._caches: dict[str, LRUCache] = {}

    def get_cache(self, model_name: str) -> LRUCache:
        """Get or create cache for specific model."""
        if model_name not in self._caches:
            self._caches[model_name] = LRUCache()
        return self._caches[model_name]

    def cache_key(self, model_name: str, operation: str, **kwargs) -> str:
        """Generate cache key for model operation."""
        config = get_config()
        key_parts = [
            config.cache.cache_key_prefix,
            model_name,
            operation,
        ]

        # Sort kwargs for consistent key generation
        sorted_kwargs = sorted(kwargs.items())
        for k, v in sorted_kwargs:
            if isinstance(v, list | dict):
                v = json.dumps(v, sort_keys=True)
            key_parts.append(f"{k}:{v}")

        key = ":".join(str(part) for part in key_parts)

        # Hash if key is too long
        if len(key) > 250:
            key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
            key = f"{key_parts[0]}:{key_parts[1]}:{key_parts[2]}:{key_hash}"

        return key

    def get(self, model_name: str, operation: str, **kwargs) -> Any | None:
        """Get cached model operation result."""
        cache = self.get_cache(model_name)
        key = self.cache_key(model_name, operation, **kwargs)
        return cache.get(key)

    def set(
        self, model_name: str, operation: str, value: Any, ttl: int | None = None, **kwargs
    ) -> None:
        """Cache model operation result."""
        cache = self.get_cache(model_name)
        key = self.cache_key(model_name, operation, **kwargs)
        cache.set(key, value, ttl)

    def invalidate_model(self, model_name: str) -> None:
        """Invalidate all cache entries for a model."""
        if model_name in self._caches:
            self._caches[model_name].clear()

    def invalidate_operation(self, model_name: str, operation: str) -> int:
        """Invalidate all cache entries for a specific operation."""
        cache = self.get_cache(model_name)
        prefix = self.cache_key(model_name, operation)
        return cache.invalidate_prefix(prefix)

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all model caches."""
        return {
            model_name: cache.get_stats()
            for model_name, cache in self._caches.items()
            if cache.get_stats() is not None
        }


# Global model cache instance
_model_cache = ModelCache()


def cache_model_operation(
    model_name: str | None = None,
    operation: str | None = None,
    ttl: int | None = None,
    key_params: list[str] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for caching model operations.

    Args:
        model_name: Model name (if None, uses class name)
        operation: Operation name (if None, uses function name)
        ttl: Time to live in seconds
        key_params: List of parameter names to include in cache key
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            config = get_config()
            if not config.features.enable_caching:
                return func(*args, **kwargs)

            # Determine model name and operation
            actual_model_name = model_name
            if actual_model_name is None and args and hasattr(args[0], "__class__"):
                actual_model_name = args[0].__class__.__name__
            elif actual_model_name is None:
                actual_model_name = "default"

            actual_operation = operation or func.__name__

            # Build cache key kwargs
            cache_kwargs = {}
            if key_params:
                # Get values from function arguments
                import inspect

                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                for param in key_params:
                    if param in bound_args.arguments:
                        cache_kwargs[param] = bound_args.arguments[param]

            # Try to get from cache
            cached_value = _model_cache.get(actual_model_name, actual_operation, **cache_kwargs)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            _model_cache.set(actual_model_name, actual_operation, result, ttl, **cache_kwargs)

            return result

        return wrapper

    return decorator


def invalidate_cache(model_name: str, operation: str | None = None) -> None:
    """Invalidate cache entries."""
    if operation:
        _model_cache.invalidate_operation(model_name, operation)
    else:
        _model_cache.invalidate_model(model_name)


def get_cache_stats() -> dict[str, dict[str, Any]]:
    """Get cache statistics."""
    return _model_cache.get_all_stats()


class CachedProperty:
    """Decorator for cached properties on model instances."""

    def __init__(self, ttl: int | None = None):
        self.ttl = ttl
        self.cache_attr_name = None

    def __set_name__(self, owner, name):
        self.cache_attr_name = f"_cached_{name}"
        self.timestamp_attr_name = f"_cached_{name}_timestamp"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        # Check if cached value exists and is not expired
        if hasattr(obj, self.cache_attr_name):
            if self.ttl is None or self.ttl <= 0:
                return getattr(obj, self.cache_attr_name)

            timestamp = getattr(obj, self.timestamp_attr_name, 0)
            if time.time() - timestamp < self.ttl:
                return getattr(obj, self.cache_attr_name)

        # Compute value
        value = self.func(obj)

        # Cache it
        setattr(obj, self.cache_attr_name, value)
        setattr(obj, self.timestamp_attr_name, time.time())

        return value

    def __call__(self, func):
        """Make the decorator callable."""
        self.func = func
        return self


# Export cache functionality
__all__ = [
    "CacheStats",
    "CachedProperty",
    "LRUCache",
    "ModelCache",
    "cache_model_operation",
    "get_cache_stats",
    "invalidate_cache",
]
