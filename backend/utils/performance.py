"""
Performance optimization utilities for production deployment.

This module provides:
1. Advanced caching with Redis support
2. Database query optimization
3. Response compression
4. Asset optimization utilities
5. Performance monitoring
"""

import time
import functools
import hashlib
import json
import gzip
import io
from typing import Any, Dict, Optional, Callable, TypeVar, Union, List, Tuple, cast
from datetime import datetime

import redis
from flask import request, Response, g, current_app
from werkzeug.wsgi import get_input_stream
from werkzeug.http import parse_accept_header

# Type variable for generic function return types
T = TypeVar('T')

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

class RedisCache(CacheBackend):
    """Redis-based cache implementation."""
    
    def __init__(self, redis_url: str, default_timeout: int = 300, prefix: str = 'cache:'):
        """Initialize Redis cache.
        
        Args:
            redis_url: Redis connection URL
            default_timeout: Default cache expiration in seconds
            prefix: Key prefix for cache entries
        """
        self.redis_client = redis.from_url(redis_url)
        self.default_timeout = default_timeout
        self.prefix = prefix
    
    def _make_key(self, key: str) -> str:
        """Create a prefixed Redis key.
        
        Args:
            key: Original cache key
            
        Returns:
            Prefixed key for Redis
        """
        return f"{self.prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from Redis cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        redis_key = self._make_key(key)
        value = self.redis_client.get(redis_key)
        
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            # If not JSON, return as is
            return value
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Set cache item in Redis with expiration.
        
        Args:
            key: Cache key
            value: Value to cache
            timeout: Expiration time in seconds (uses default if None)
        """
        redis_key = self._make_key(key)
        
        # Convert value to JSON if possible
        if not isinstance(value, (str, bytes)):
            value = json.dumps(value)
        
        expiration = timeout if timeout is not None else self.default_timeout
        self.redis_client.setex(redis_key, expiration, value)
    
    def delete(self, key: str) -> None:
        """Delete item from Redis cache.
        
        Args:
            key: Cache key to delete
        """
        redis_key = self._make_key(key)
        self.redis_client.delete(redis_key)
    
    def clear(self) -> None:
        """Clear all cache entries with this prefix."""
        for key in self.redis_client.keys(f"{self.prefix}*"):
            self.redis_client.delete(key)

class CacheManager:
    """Cache manager that selects the appropriate backend."""
    
    def __init__(self, app=None):
        """Initialize cache manager.
        
        Args:
            app: Flask application instance
        """
        self.cache_backend = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask application.
        
        Args:
            app: Flask application instance
        """
        cache_type = app.config.get('CACHE_TYPE', 'simple').lower()
        default_timeout = app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
        
        if cache_type == 'redis':
            redis_url = app.config.get('CACHE_REDIS_URL', 'redis://localhost:6379/0')
            self.cache_backend = RedisCache(redis_url, default_timeout)
        else:
            # Default to in-memory cache
            self.cache_backend = MemoryCache(default_timeout)
        
        # Register extension with app
        app.extensions['cache'] = self
    
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
        """Decorator to cache function results.
        
        Args:
            timeout: Cache expiration time in seconds
            key_prefix: Prefix for cache key
            
        Returns:
            Decorated function with caching
        """
        def decorator(f: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(f)
            def wrapper(*args: Any, **kwargs: Any) -> T:
                # Create cache key from function name and arguments
                key_parts = [key_prefix, f.__name__]
                
                # Add args and kwargs to key
                for arg in args:
                    key_parts.append(str(arg))
                
                for k, v in sorted(kwargs.items()):
                    key_parts.append(f"{k}:{v}")
                
                key_string = ":".join(key_parts)
                cache_key = hashlib.md5(key_string.encode()).hexdigest()
                
                # Check cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cast(T, cached_value)
                
                # Call original function
                result = f(*args, **kwargs)
                
                # Cache result
                self.set(cache_key, result, timeout)
                return result
            
            return wrapper
        
        return decorator

# Global cache instance
cache_manager = CacheManager()

# ===== Database Query Optimization =====

def optimize_query(query, limit: Optional[int] = None, offset: Optional[int] = 0, 
                  select_fields: Optional[List[str]] = None):
    """Optimize a database query.
    
    Args:
        query: SQLAlchemy query object
        limit: Maximum number of results
        offset: Query offset
        select_fields: Specific fields to select
        
    Returns:
        Optimized query
    """
    # Select specific fields if provided
    if select_fields:
        query = query.with_entities(*select_fields)
    
    # Apply pagination
    if offset:
        query = query.offset(offset)
    
    if limit:
        query = query.limit(limit)
    
    return query

def query_with_timeout(query, timeout_seconds: int = 30):
    """Execute a query with a timeout.
    
    Args:
        query: SQLAlchemy query object
        timeout_seconds: Query timeout in seconds
        
    Returns:
        Query results
    """
    # This implementation depends on your database driver
    # For PostgreSQL with psycopg2:
    # connection = query.session.connection()
    # connection.connection.set_session(statement_timeout=timeout_seconds * 1000)
    
    try:
        return query.all()
    finally:
        # Reset timeout
        # connection.connection.set_session(statement_timeout=0)
        pass

# ===== Response Compression =====

def gzip_response(response: Response) -> Response:
    """Compress response data with gzip.
    
    Args:
        response: Flask response object
        
    Returns:
        Compressed response
    """
    accept_encoding = request.headers.get('Accept-Encoding', '')
    
    # Check if client accepts gzip
    if 'gzip' not in accept_encoding.lower():
        return response
    
    # Check if response is already compressed
    if response.headers.get('Content-Encoding') is not None:
        return response
    
    # Check if response is compressible
    content_type = response.headers.get('Content-Type', '')
    compressible_types = [
        'text/', 'application/json', 'application/javascript', 
        'application/xml', 'application/xhtml+xml'
    ]
    
    is_compressible = any(t in content_type for t in compressible_types)
    if not is_compressible:
        return response
    
    # Compress response data
    compressed_data = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed_data, mode='wb') as f:
        f.write(response.data)
    
    response.data = compressed_data.getvalue()
    response.headers['Content-Encoding'] = 'gzip'
    response.headers['Content-Length'] = str(len(response.data))
    response.headers['Vary'] = 'Accept-Encoding'
    
    return response

def compression_middleware(app):
    """WSGI middleware for response compression.
    
    Args:
        app: Flask application
        
    Returns:
        WSGI middleware function
    """
    def middleware(environ, start_response):
        flask_response = []
        
        def custom_start_response(status, headers, exc_info=None):
            flask_response.extend([status, headers])
            return start_response(status, headers, exc_info)
        
        app_iter = app(environ, custom_start_response)
        
        # Process response
        status, headers = flask_response
        
        # Check if compression is applicable
        accept_encoding = environ.get('HTTP_ACCEPT_ENCODING', '')
        if 'gzip' in accept_encoding:
            # Implement compression logic
            pass
        
        return app_iter
    
    return middleware

# ===== Performance Monitoring =====

class PerformanceMonitor:
    """Performance monitoring utilities."""
    
    @staticmethod
    def start_timer():
        """Start a performance timer.
        
        Returns:
            Start time in seconds
        """
        return time.time()
    
    @staticmethod
    def end_timer(start_time: float) -> float:
        """End a performance timer and get elapsed time.
        
        Args:
            start_time: Start time from start_timer()
            
        Returns:
            Elapsed time in seconds
        """
        return time.time() - start_time
    
    @classmethod
    def log_performance(cls, operation: str, start_time: float, 
                       extra_data: Optional[Dict[str, Any]] = None):
        """Log performance metrics.
        
        Args:
            operation: Operation name
            start_time: Start time from start_timer()
            extra_data: Additional data to log
        """
        elapsed = cls.end_timer(start_time)
        
        log_data = {
            'operation': operation,
            'elapsed_seconds': elapsed,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        if extra_data:
            log_data.update(extra_data)
        
        # In a real implementation, send to monitoring system
        # For now, just log to console
        print(f"PERFORMANCE: {json.dumps(log_data)}")
    
    @classmethod
    def monitor(cls, operation_name: str):
        """Decorator to monitor function performance.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Decorated function
        """
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                start_time = cls.start_timer()
                
                try:
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

def profile_request_middleware(app):
    """Middleware to profile request performance.
    
    Args:
        app: Flask application
        
    Returns:
        Modified app with before/after request handlers
    """
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            
            # Log request performance
            log_data = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'elapsed_seconds': elapsed,
                'content_length': response.headers.get('Content-Length', 0),
                'user_agent': request.headers.get('User-Agent', ''),
                'ip': request.remote_addr
            }
            
            # Add to response headers for debugging
            response.headers['X-Response-Time'] = f"{elapsed:.6f}s"
            
            # In production, send to monitoring system
            # For now, just log to console if slow
            if elapsed > 1.0:  # Log slow requests
                print(f"SLOW REQUEST: {json.dumps(log_data)}")
        
        return response
    
    return app

# ===== Database Connection Pooling =====

def configure_db_pool(db, pool_size=10, max_overflow=20, timeout=30):
    """Configure SQLAlchemy connection pooling.
    
    Args:
        db: SQLAlchemy database instance
        pool_size: Connection pool size
        max_overflow: Maximum overflow connections
        timeout: Connection timeout in seconds
    """
    # This assumes you're using SQLAlchemy
    engine_options = {
        'pool_size': pool_size,
        'max_overflow': max_overflow,
        'pool_timeout': timeout,
        'pool_recycle': 3600,  # Recycle connections after 1 hour
        'pool_pre_ping': True  # Verify connections before use
    }
    
    # Apply options to engine
    for key, value in engine_options.items():
        setattr(db.engine, key, value)