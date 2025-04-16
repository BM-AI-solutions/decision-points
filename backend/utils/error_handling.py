"""
Enhanced error handling and logging for production deployment.

This module provides:
1. Structured error handling
2. Error tracking and monitoring
3. Custom exception classes
4. Global error handlers
5. Error reporting
"""

import os
import sys
import traceback
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Callable, Type, Union
from functools import wraps

from flask import request, jsonify, current_app, g, Response

from utils.logger import setup_logger

# Set up module logger
logger = setup_logger('utils.error_handling')

# ===== Custom Exception Classes =====

class AppError(Exception):
    """Base exception class for application errors."""
    
    def __init__(self, message: str, status_code: int = 500, error_code: Optional[str] = None, 
                details: Optional[Dict[str, Any]] = None):
        """Initialize application error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Application-specific error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or 'internal_error'
        self.details = details or {}
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()

class ValidationError(AppError):
    """Exception for data validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                details: Optional[Dict[str, Any]] = None):
        """Initialize validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
            details: Additional error details
        """
        error_details = details or {}
        if field:
            error_details['field'] = field
        
        super().__init__(
            message=message,
            status_code=400,
            error_code='validation_error',
            details=error_details
        )

class AuthenticationError(AppError):
    """Exception for authentication errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                details: Optional[Dict[str, Any]] = None):
        """Initialize authentication error.
        
        Args:
            message: Error message
            error_code: Specific authentication error code
            details: Additional error details
        """
        super().__init__(
            message=message,
            status_code=401,
            error_code=error_code or 'authentication_error',
            details=details or {}
        )

class AuthorizationError(AppError):
    """Exception for authorization errors."""
    
    def __init__(self, message: str, resource: Optional[str] = None, 
                details: Optional[Dict[str, Any]] = None):
        """Initialize authorization error.
        
        Args:
            message: Error message
            resource: Resource that access was denied to
            details: Additional error details
        """
        error_details = details or {}
        if resource:
            error_details['resource'] = resource
        
        super().__init__(
            message=message,
            status_code=403,
            error_code='authorization_error',
            details=error_details
        )

class ResourceNotFoundError(AppError):
    """Exception for resource not found errors."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, 
                resource_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Initialize resource not found error.
        
        Args:
            message: Error message
            resource_type: Type of resource not found
            resource_id: ID of resource not found
            details: Additional error details
        """
        error_details = details or {}
        if resource_type:
            error_details['resource_type'] = resource_type
        if resource_id:
            error_details['resource_id'] = resource_id
        
        super().__init__(
            message=message,
            status_code=404,
            error_code='resource_not_found',
            details=error_details
        )

class RateLimitError(AppError):
    """Exception for rate limiting errors."""
    
    def __init__(self, message: str, limit: Optional[int] = None, 
                reset_time: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        """Initialize rate limit error.
        
        Args:
            message: Error message
            limit: Rate limit
            reset_time: When rate limit resets (timestamp)
            details: Additional error details
        """
        error_details = details or {}
        if limit:
            error_details['limit'] = limit
        if reset_time:
            error_details['reset_time'] = reset_time
        
        super().__init__(
            message=message,
            status_code=429,
            error_code='rate_limit_exceeded',
            details=error_details
        )

class ServiceUnavailableError(AppError):
    """Exception for service unavailable errors."""
    
    def __init__(self, message: str, service: Optional[str] = None, 
                retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        """Initialize service unavailable error.
        
        Args:
            message: Error message
            service: Unavailable service name
            retry_after: Seconds to wait before retrying
            details: Additional error details
        """
        error_details = details or {}
        if service:
            error_details['service'] = service
        if retry_after:
            error_details['retry_after'] = retry_after
        
        super().__init__(
            message=message,
            status_code=503,
            error_code='service_unavailable',
            details=error_details
        )

class DatabaseError(AppError):
    """Exception for database errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None, 
                details: Optional[Dict[str, Any]] = None):
        """Initialize database error.
        
        Args:
            message: Error message
            operation: Database operation that failed
            details: Additional error details
        """
        error_details = details or {}
        if operation:
            error_details['operation'] = operation
        
        super().__init__(
            message=message,
            status_code=500,
            error_code='database_error',
            details=error_details
        )

class ExternalServiceError(AppError):
    """Exception for external service errors."""
    
    def __init__(self, message: str, service: str, status_code: Optional[int] = None, 
                details: Optional[Dict[str, Any]] = None):
        """Initialize external service error.
        
        Args:
            message: Error message
            service: External service name
            status_code: HTTP status code from external service
            details: Additional error details
        """
        error_details = details or {}
        error_details['service'] = service
        if status_code:
            error_details['status_code'] = status_code
        
        super().__init__(
            message=message,
            status_code=502,
            error_code='external_service_error',
            details=error_details
        )

# ===== Error Handling Utilities =====

def format_exception(exc: Exception) -> Dict[str, Any]:
    """Format exception details for logging and reporting.
    
    Args:
        exc: Exception object
        
    Returns:
        Formatted exception details
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    # Format traceback
    tb_frames = traceback.extract_tb(exc_traceback)
    formatted_frames = []
    
    for frame in tb_frames:
        formatted_frames.append({
            'filename': frame.filename,
            'lineno': frame.lineno,
            'name': frame.name,
            'line': frame.line
        })
    
    # Get exception details
    if isinstance(exc, AppError):
        error_details = {
            'error_id': exc.error_id,
            'message': exc.message,
            'status_code': exc.status_code,
            'error_code': exc.error_code,
            'details': exc.details,
            'timestamp': exc.timestamp
        }
    else:
        error_details = {
            'error_id': str(uuid.uuid4()),
            'message': str(exc),
            'status_code': 500,
            'error_code': 'internal_error',
            'details': {},
            'timestamp': datetime.utcnow().isoformat()
        }
    
    # Add traceback and exception type
    error_details['traceback'] = formatted_frames
    error_details['exception_type'] = exc_type.__name__ if exc_type else type(exc).__name__
    
    # Add request information if available
    if request:
        error_details['request'] = {
            'url': request.url,
            'method': request.method,
            'headers': dict(request.headers),
            'remote_addr': request.remote_addr
        }
    
    return error_details

def log_exception(exc: Exception, log_level: int = logging.ERROR) -> str:
    """Log exception details.
    
    Args:
        exc: Exception object
        log_level: Logging level
        
    Returns:
        Error ID for reference
    """
    error_details = format_exception(exc)
    error_id = error_details['error_id']
    
    # Log basic error info
    logger.log(
        log_level,
        f"Error {error_id}: {error_details['message']} "
        f"({error_details['exception_type']})"
    )
    
    # Log detailed error info at debug level
    logger.debug(f"Detailed error {error_id}: {json.dumps(error_details)}")
    
    return error_id

def report_exception(exc: Exception) -> None:
    """Report exception to external error tracking service.
    
    Args:
        exc: Exception object
    """
    error_details = format_exception(exc)
    
    # In a real implementation, send to error tracking service
    # For example, Sentry, Rollbar, etc.
    # For now, just log to console
    print(f"ERROR REPORT: {json.dumps(error_details)}")

def error_response(exc: Exception) -> Response:
    """Create a JSON response for an exception.
    
    Args:
        exc: Exception object
        
    Returns:
        Flask JSON response
    """
    if isinstance(exc, AppError):
        status_code = exc.status_code
        error_data = {
            'error': exc.error_code,
            'message': exc.message,
            'error_id': exc.error_id,
            'status': status_code
        }
        
        # Include details in development mode
        if current_app.debug:
            error_data['details'] = exc.details
    else:
        status_code = 500
        error_id = log_exception(exc)
        error_data = {
            'error': 'internal_error',
            'message': 'An unexpected error occurred',
            'error_id': error_id,
            'status': status_code
        }
        
        # Include exception details in development mode
        if current_app.debug:
            error_data['exception'] = str(exc)
            error_data['traceback'] = traceback.format_exc()
    
    return jsonify(error_data), status_code

# ===== Error Handling Decorators =====

def handle_exceptions(f):
    """Decorator to handle exceptions in route handlers.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AppError as e:
            # Log application errors
            log_exception(e)
            return error_response(e)
        except Exception as e:
            # Log and report unexpected errors
            log_exception(e)
            report_exception(e)
            return error_response(e)
    
    return decorated_function

def setup_error_handlers(app):
    """Set up global error handlers for a Flask app.
    
    Args:
        app: Flask application
    """
    @app.errorhandler(400)
    def bad_request(e):
        return error_response(ValidationError(str(e)))
    
    @app.errorhandler(401)
    def unauthorized(e):
        return error_response(AuthenticationError(str(e)))
    
    @app.errorhandler(403)
    def forbidden(e):
        return error_response(AuthorizationError(str(e)))
    
    @app.errorhandler(404)
    def not_found(e):
        return error_response(ResourceNotFoundError(str(e)))
    
    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return error_response(RateLimitError(str(e)))
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return error_response(e)
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log and report unexpected errors
        log_exception(e)
        report_exception(e)
        return error_response(e)

# ===== Error Monitoring =====

class ErrorMonitor:
    """Error monitoring and tracking utilities."""
    
    @staticmethod
    def capture_exception(exc: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """Capture and report an exception.
        
        Args:
            exc: Exception object
            context: Additional context information
            
        Returns:
            Error ID for reference
        """
        error_details = format_exception(exc)
        
        # Add additional context
        if context:
            error_details['context'] = context
        
        # Log the error
        error_id = log_exception(exc)
        
        # Report to error tracking service
        report_exception(exc)
        
        return error_id
    
    @staticmethod
    def capture_message(message: str, level: str = 'error', 
                       context: Optional[Dict[str, Any]] = None) -> str:
        """Capture and report a message.
        
        Args:
            message: Message to capture
            level: Log level (error, warning, info)
            context: Additional context information
            
        Returns:
            Message ID for reference
        """
        message_id = str(uuid.uuid4())
        
        # Create message details
        message_details = {
            'message_id': message_id,
            'message': message,
            'level': level,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add additional context
        if context:
            message_details['context'] = context
        
        # Add request information if available
        if request:
            message_details['request'] = {
                'url': request.url,
                'method': request.method,
                'remote_addr': request.remote_addr
            }
        
        # Log the message
        log_func = getattr(logger, level, logger.error)
        log_func(f"{level.upper()}: {message} (ID: {message_id})")
        
        # In a real implementation, send to error tracking service
        # For now, just log to console
        print(f"MESSAGE CAPTURE: {json.dumps(message_details)}")
        
        return message_id
    
    @staticmethod
    def monitor(f):
        """Decorator to monitor function for errors.
        
        Args:
            f: Function to decorate
            
        Returns:
            Decorated function
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                # Capture exception with function context
                context = {
                    'function': f.__name__,
                    'module': f.__module__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                }
                ErrorMonitor.capture_exception(e, context)
                raise
        
        return decorated_function