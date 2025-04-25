"""
Performance optimization utilities for production deployment.

This module provides:
1. Advanced caching with Redis support
2. Database query optimization utilities
3. Notes on response compression (to be implemented via FastAPI middleware)
4. Asset optimization utilities (Placeholder)
5. Performance monitoring utilities
"""

import time
import functools
import hashlib
import json
import gzip
import io
import redis # Ensure redis package is installed
import asyncio # Added for async checks
from typing import Any, Dict, Optional, Callable, TypeVar, Union, List, Tuple, cast
from datetime import datetime

# Replaced Flask imports with FastAPI/Starlette
from fastapi import Request, Response # Response might be needed for type hints if adapting functions

# Removed Werkzeug imports

# Type variable for generic function return types
T = TypeVar('T')

# Import logger
from utils.logger import setup_logger
logger = setup_logger('utils.performance')


# ===== Advanced Caching =====

class CacheBackend:
    """Abstract base class for cache backends."""

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        raise NotImplementedError

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Set cache item with expiration."""
        raise NotImplementedError

    def delete(self, key: str) -> None:
        """Delete item from cache."""
        raise NotImplementedError

    def clear(self) -> None:
        """Clear all cache entries."""
        raise NotImplementedError

class MemoryCache(CacheBackend):
    """In-memory cache implementation."""

    def __init__(self, default_timeout: int = 300):
        """Initialize cache."""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_timeout = default_timeout

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache if it exists and hasn't expired."""
        entry = self._cache.get(key)
        if entry is None:
            return None

        if entry['expires_at'] < time.time():
            # Expired, remove from cache
            if key in self._cache: # Check again in case of race condition
                 del self._cache[key]
            return None

        return entry['value']

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Set cache item with expiration."""
        expires_at = time.time() + (timeout if timeout is not None else self.default_timeout)
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at
        }

    def delete(self, key: str) -> None:
        """Delete item from cache."""
        if key in self._cache:
            try:
                del self._cache[key]
            except KeyError:
                 pass # Ignore if key was deleted between check and delete

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

class RedisCache(CacheBackend):
    """Redis-based cache implementation."""

    def __init__(self, redis_url: str, default_timeout: int = 300, prefix: str = 'cache:'):
        """Initialize Redis cache."""
        try:
            # decode_responses=True simplifies getting strings back from Redis
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping() # Check connection
            logger.info(f"Redis cache connected successfully to {redis_url}")
        except redis.exceptions.ConnectionError as e:
             logger.error(f"Failed to connect to Redis at {redis_url}: {e}")
             # Consider raising an error or falling back to MemoryCache if appropriate
             raise ConnectionError(f"Failed to connect to Redis: {e}") from e

        self.default_timeout = default_timeout
        self.prefix = prefix

    def _make_key(self, key: str) -> str:
        """Create a prefixed Redis key."""
        return f"{self.prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """Get item from Redis cache."""
        redis_key = self._make_key(key)
        try:
            value = self.redis_client.get(redis_key)
            if value is None:
                return None
            # Attempt to decode JSON, otherwise return raw string
            try:
                # Assuming strings that are valid JSON should be parsed
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                 # If not valid JSON or not a string type for loads, return as is
                 return value
        except redis.exceptions.RedisError as e:
             logger.error(f"Redis GET error for key '{redis_key}': {e}")
             return None


    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Set cache item in Redis with expiration."""
        redis_key = self._make_key(key)
        expiration = timeout if timeout is not None else self.default_timeout

        # Serialize non-string/bytes values to JSON
        if not isinstance(value, (str, bytes, int, float)): # Allow numbers directly
            try:
                serialized_value = json.dumps(value)
            except TypeError as e:
                 logger.error(f"Failed to serialize value for Redis key '{redis_key}': {e}")
                 return # Don't cache unserializable data
        else:
             serialized_value = value

        try:
            # Use expiration in seconds directly with setex
            self.redis_client.setex(redis_key, expiration, serialized_value)
        except redis.exceptions.RedisError as e:
             logger.error(f"Redis SETEX error for key '{redis_key}': {e}")


    def delete(self, key: str) -> None:
        """Delete item from Redis cache."""
        redis_key = self._make_key(key)
        try:
            self.redis_client.delete(redis_key)
        except redis.exceptions.RedisError as e:
             logger.error(f"Redis DELETE error for key '{redis_key}': {e}")


    def clear(self) -> None:
        """Clear all cache entries with this prefix (use with caution)."""
        try:
            # Use scan_iter for potentially large numbers of keys to avoid blocking
            keys_to_delete = [key for key in self.redis_client.scan_iter(f"{self.prefix}*")]
            if keys_to_delete:
                # Delete keys in chunks if there are many, to avoid command length limits
                chunk_size = 500
                for i in range(0, len(keys_to_delete), chunk_size):
                     chunk = keys_to_delete[i:i + chunk_size]
                     self.redis_client.delete(*chunk)
                logger.info(f"Cleared {len(keys_to_delete)} keys with prefix '{self.prefix}'")
            else:
                 logger.info(f"No keys found with prefix '{self.prefix}' to clear.")
        except redis.exceptions.RedisError as e:
             logger.error(f"Redis CLEAR (delete keys) error for prefix '{self.prefix}': {e}")


class CacheManager:
    """Cache manager that holds a configured cache backend."""
    # Removed Flask app integration from __init__ and init_app

    def __init__(self, backend: CacheBackend):
        """Initialize cache manager with a specific backend."""
        if not isinstance(backend, CacheBackend):
             raise TypeError("backend must be an instance of CacheBackend")
        self.cache_backend = backend
        logger.info(f"CacheManager initialized with backend: {type(backend).__name__}")

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        return self.cache_backend.get(key)

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Set cache item with expiration."""
        self.cache_backend.set(key, value, timeout)

    def delete(self, key: str) -> None:
        """Delete item from cache."""
        self.cache_backend.delete(key)

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache_backend.clear()

    def cached(self, timeout: Optional[int] = None, key_prefix: str = ''):
        """Decorator to cache function results."""
        def decorator(f: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(f)
            async def wrapper(*args: Any, **kwargs: Any) -> T: # Make wrapper async
                # Create cache key from function name and arguments
                # Consider using a more robust serialization method if args/kwargs are complex
                key_parts = [key_prefix, f.__module__, f.__name__]

                # Add args and kwargs to key
                try:
                    # Attempt to serialize args/kwargs reliably using default=str for non-serializable
                    args_repr = json.dumps(args, sort_keys=True, default=str)
                    kwargs_repr = json.dumps(kwargs, sort_keys=True, default=str)
                    key_parts.extend([args_repr, kwargs_repr])
                except TypeError:
                     # Fallback for truly unserializable args/kwargs (less precise)
                     logger.warning(f"Could not JSON serialize args/kwargs for cache key of {f.__name__}. Using str().")
                     key_parts.extend(map(str, args))
                     key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))


                key_string = ":".join(key_parts)
                # Use sha256 for potentially longer keys and better distribution
                cache_key = hashlib.sha256(key_string.encode()).hexdigest()

                # Check cache
                # Note: Accessing self (CacheManager instance) requires it to be available.
                # This typically means the instance is created globally or injected via dependency.
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache HIT for key: {cache_key} ({f.__name__})")
                    return cast(T, cached_value)
                else:
                     logger.debug(f"Cache MISS for key: {cache_key} ({f.__name__})")


                # Call original function (await if it's async)
                if asyncio.iscoroutinefunction(f):
                    result = await f(*args, **kwargs)
                else:
                     # Run sync function in thread pool if in async context?
                     # For simplicity, assume sync functions are okay or handled elsewhere.
                     result = f(*args, **kwargs)


                # Cache result
                self.set(cache_key, result, timeout)
                return result

            return wrapper
        return decorator

# TODO: Instantiate CacheManager during FastAPI app startup based on config.
# Example (in main.py or config module):
# from .utils.performance import CacheManager, MemoryCache, RedisCache
# settings = ... # Load settings
# try:
#     if settings.CACHE_TYPE == 'redis' and settings.CACHE_REDIS_URL:
#         cache_backend = RedisCache(redis_url=settings.CACHE_REDIS_URL, default_timeout=settings.CACHE_DEFAULT_TIMEOUT)
#     else:
#         logger.info("Using MemoryCache (Redis not configured or CACHE_TYPE != 'redis')")
#         cache_backend = MemoryCache(default_timeout=settings.CACHE_DEFAULT_TIMEOUT)
# except ConnectionError:
#      logger.error("Redis connection failed, falling back to MemoryCache.")
#      cache_backend = MemoryCache(default_timeout=settings.CACHE_DEFAULT_TIMEOUT)
#
# cache_manager = CacheManager(backend=cache_backend)
#
# # Then use `cache_manager` instance, potentially via dependency injection:
# def get_cache() -> CacheManager:
#      # This assumes cache_manager is accessible in this scope (e.g., global or app state)
#      return cache_manager
#
# @app.get("/data")
# @cache_manager.cached(timeout=60) # Apply decorator
# async def get_data(cache: CacheManager = Depends(get_cache)): # Inject if needed inside
#      # ... function logic ...
#      pass

# ===== Database Query Optimization =====
# These utilities might need adaptation based on the ORM used with FastAPI (e.g., SQLAlchemy async)

def optimize_query(query: Any, limit: Optional[int] = None, offset: Optional[int] = 0,
                  select_fields: Optional[List[str]] = None) -> Any:
    """Optimize a database query (basic example)."""
    # This is highly dependent on the ORM being used.
    # Example for SQLAlchemy (sync):
    # if select_fields and hasattr(query, 'with_entities'):
    #     # This needs model attributes (e.g., User.id, User.name), not just strings
    #     # You'd need to map field names to model attributes.
    #     model_attrs = [getattr(query.column_descriptions[0]['entity'], field) for field in select_fields]
    #     query = query.with_entities(*model_attrs)
    if hasattr(query, 'offset'):
        query = query.offset(offset)
    if hasattr(query, 'limit'):
        query = query.limit(limit)
    return query

# query_with_timeout is complex and depends heavily on DB driver and async context.
# It's generally better handled by configuring timeouts at the engine or session level.

# ===== Response Compression =====
# Removed Flask-specific gzip_response and compression_middleware.
# TODO: Use FastAPI's GZipMiddleware in your main application setup.
# Example (in main.py):
# from fastapi.middleware.gzip import GZipMiddleware
# app.add_middleware(GZipMiddleware, minimum_size=1000) # Compress responses > 1000 bytes

# ===== Performance Monitoring =====

class PerformanceMonitor:
    """Performance monitoring utilities."""

    @staticmethod
    def start_timer() -> float:
        """Start a performance timer."""
        return time.perf_counter() # Use perf_counter for higher resolution

    @staticmethod
    def end_timer(start_time: float) -> float:
        """End a performance timer and get elapsed time in milliseconds."""
        return (time.perf_counter() - start_time) * 1000 # Return ms

    @classmethod
    def log_performance(cls, operation: str, start_time: float,
                       extra_data: Optional[Dict[str, Any]] = None):
        """Log performance metrics."""
        elapsed_ms = cls.end_timer(start_time)

        log_data = {
            'operation': operation,
            'elapsed_ms': round(elapsed_ms, 2), # Log in ms, rounded
            'timestamp': datetime.utcnow().isoformat(),
        }

        if extra_data:
            log_data.update(extra_data)

        # TODO: Integrate with a proper monitoring system (e.g., Prometheus, Datadog)
        logger.info(f"PERFORMANCE: {json.dumps(log_data)}")


    @classmethod
    def monitor(cls, operation_name: str):
        """Decorator to monitor function performance."""
        def decorator(f):
            @functools.wraps(f)
            async def wrapper(*args, **kwargs): # Make async
                start_time = cls.start_timer()
                try:
                    # Await if the wrapped function is async
                    if asyncio.iscoroutinefunction(f):
                         result = await f(*args, **kwargs)
                    else:
                         # Consider running sync functions in a thread pool for non-blocking IO
                         # For simplicity here, we call it directly.
                         result = f(*args, **kwargs)
                    cls.log_performance(operation_name, start_time)
                    return result
                except Exception as e:
                    cls.log_performance(
                        operation_name,
                        start_time,
                        {'error': str(e), 'error_type': type(e).__name__}
                    )
                    raise
            return wrapper
        return decorator

# ===== Request Profiling =====
# Removed Flask-specific profile_request_middleware.
# TODO: Implement request profiling using FastAPI middleware.
# Example (in main.py):
# from starlette.middleware.base import BaseHTTPMiddleware
# class ProfilingMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         start_time = time.perf_counter()
#         response = await call_next(request)
#         process_time_ms = (time.perf_counter() - start_time) * 1000
#         response.headers["X-Process-Time-Ms"] = str(process_time_ms)
#         # Log detailed info if needed, consider sampling for high traffic
#         if process_time_ms > 500: # Example: Log only slow requests
#              logger.info(f"Slow Request: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time_ms:.2f}ms")
#         return response
# app.add_middleware(ProfilingMiddleware)


# ===== Database Connection Pooling =====
# This function might still be relevant depending on how SQLAlchemy is configured,
# but the configuration typically happens during app startup, not via a utility function like this.

def configure_db_pool(engine: Any, pool_size=10, max_overflow=20, timeout=30): # Accept engine directly
    """Configure database connection pooling (Example for SQLAlchemy)."""
    # This is highly specific to the ORM and engine configuration.
    # For SQLAlchemy, these are usually set during create_engine.
    logger.warning("configure_db_pool is likely deprecated. Pooling should be configured during engine creation.")
    # Example of how it *might* be done if engine allows runtime changes (uncommon and potentially unsafe)
    # if hasattr(engine, 'pool'):
    #     try:
    #         # Modifying pool parameters at runtime can be complex and driver-specific
    #         # engine.pool._size = pool_size # Example, likely incorrect/unsafe
    #         pass
    #     except Exception as e:
    #          logger.error(f"Failed to dynamically configure DB pool: {e}")
    pass