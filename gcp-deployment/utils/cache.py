import functools
import time
import json
import hashlib
from typing import Any, Dict, Optional, Callable, TypeVar, cast

T = TypeVar('T')

class SimpleCache:
    """Simple in-memory cache with expiration."""

    def __init__(self, default_timeout: int = 300):
        """Initialize cache.

        Args:
            default_timeout: Default cache expiration in seconds
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_timeout = default_timeout

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache if it exists and hasn't expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None

        entry = self._cache[key]
        if entry['expires_at'] < time.time():
            del self._cache[key]
            return None

        return entry['value']

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Set cache item with expiration.

        Args:
            key: Cache key
            value: Value to cache
            timeout: Expiration time in seconds (uses default if None)
        """
        expires_at = time.time() + (timeout if timeout is not None else self.default_timeout)
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at
        }

    def delete(self, key: str) -> None:
        """Delete item from cache.

        Args:
            key: Cache key to delete
        """
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

# Global cache instance
cache = SimpleCache()

def cached(timeout: Optional[int] = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to cache function results.

    Args:
        timeout: Cache expiration time in seconds

    Returns:
        Decorated function with caching
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Create cache key from function name and arguments
            key_parts = [func.__name__]

            # Add args and kwargs to key
            for arg in args:
                key_parts.append(str(arg))

            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}:{v}")

            key_string = ":".join(key_parts)
            cache_key = hashlib.md5(key_string.encode()).hexdigest()

            # Check cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cast(T, cached_value)

            # Call original function
            result = func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result, timeout)
            return result

        return wrapper
    return decorator