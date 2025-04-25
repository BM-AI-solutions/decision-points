"""
Enhanced error handling and logging for production deployment.

This module provides:
1. Structured error handling
2. Error tracking and monitoring
3. Custom exception classes
4. Global error handlers (to be implemented in FastAPI app)
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

# Replaced Flask imports with FastAPI/Starlette
from fastapi import Request, HTTPException
from starlette.responses import JSONResponse
# from starlette.status import * # Import specific status codes if needed

from utils.logger import setup_logger

# Set up module logger
logger = setup_logger('utils.error_handling')

# ===== Custom Exception Classes (Compatible with FastAPI) =====
# These exceptions can be raised in your application code.
# FastAPI exception handlers will catch them and return appropriate responses.

class AppError(Exception):
    """Base exception class for application errors."""

    def __init__(self, message: str, status_code: int = 500, error_code: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """Initialize application error."""
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
        """Initialize validation error."""
        error_details = details or {}
        if field:
            error_details['field'] = field

        super().__init__(
            message=message,
            status_code=400, # Bad Request
            error_code='validation_error',
            details=error_details
        )

class AuthenticationError(AppError):
    """Exception for authentication errors."""

    def __init__(self, message: str, error_code: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """Initialize authentication error."""
        super().__init__(
            message=message,
            status_code=401, # Unauthorized
            error_code=error_code or 'authentication_error',
            details=details or {}
        )

class AuthorizationError(AppError):
    """Exception for authorization errors."""

    def __init__(self, message: str, resource: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """Initialize authorization error."""
        error_details = details or {}
        if resource:
            error_details['resource'] = resource

        super().__init__(
            message=message,
            status_code=403, # Forbidden
            error_code='authorization_error',
            details=error_details
        )

class ResourceNotFoundError(AppError):
    """Exception for resource not found errors."""

    def __init__(self, message: str, resource_type: Optional[str] = None,
                 resource_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Initialize resource not found error."""
        error_details = details or {}
        if resource_type:
            error_details['resource_type'] = resource_type
        if resource_id:
            error_details['resource_id'] = resource_id

        super().__init__(
            message=message,
            status_code=404, # Not Found
            error_code='resource_not_found',
            details=error_details
        )

class RateLimitError(AppError):
    """Exception for rate limiting errors."""

    def __init__(self, message: str, limit: Optional[int] = None,
                 reset_time: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        """Initialize rate limit error."""
        error_details = details or {}
        if limit:
            error_details['limit'] = limit
        if reset_time:
            error_details['reset_time'] = reset_time

        super().__init__(
            message=message,
            status_code=429, # Too Many Requests
            error_code='rate_limit_exceeded',
            details=error_details
        )

class ServiceUnavailableError(AppError):
    """Exception for service unavailable errors."""

    def __init__(self, message: str, service: Optional[str] = None,
                 retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        """Initialize service unavailable error."""
        error_details = details or {}
        if service:
            error_details['service'] = service
        if retry_after:
            error_details['retry_after'] = retry_after

        super().__init__(
            message=message,
            status_code=503, # Service Unavailable
            error_code='service_unavailable',
            details=error_details
        )

class DatabaseError(AppError):
    """Exception for database errors."""

    def __init__(self, message: str, operation: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """Initialize database error."""
        error_details = details or {}
        if operation:
            error_details['operation'] = operation

        super().__init__(
            message=message,
            status_code=500, # Internal Server Error
            error_code='database_error',
            details=error_details
        )

class ExternalServiceError(AppError):
    """Exception for external service errors."""

    def __init__(self, message: str, service: str, status_code: Optional[int] = None,
                 details: Optional[Dict[str, Any]] = None):
        """Initialize external service error."""
        error_details = details or {}
        error_details['service'] = service
        if status_code:
            error_details['status_code'] = status_code

        super().__init__(
            message=message,
            status_code=502, # Bad Gateway
            error_code='external_service_error',
            details=error_details
        )

# ===== Error Handling Utilities =====

def format_exception(exc: Exception, request: Optional[Request] = None) -> Dict[str, Any]:
    """Format exception details for logging and reporting.

    Args:
        exc: Exception object
        request: Optional FastAPI Request object to include request details.

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
    elif isinstance(exc, HTTPException): # Handle FastAPI's HTTPException
         error_details = {
            'error_id': str(uuid.uuid4()),
            'message': exc.detail,
            'status_code': exc.status_code,
            'error_code': 'http_exception', # Generic code for HTTPException
            'details': getattr(exc, 'details', {}), # Include custom details if added
            'timestamp': datetime.utcnow().isoformat()
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
            'url': str(request.url),
            'method': request.method,
            'headers': dict(request.headers),
            'client_host': request.client.host if request.client else None
        }

    return error_details

def log_exception(exc: Exception, request: Optional[Request] = None, log_level: int = logging.ERROR) -> str:
    """Log exception details.

    Args:
        exc: Exception object
        request: Optional FastAPI Request object.
        log_level: Logging level

    Returns:
        Error ID for reference
    """
    error_details = format_exception(exc, request)
    error_id = error_details['error_id']

    # Log basic error info
    log_message = (
        f"Error {error_id}: {error_details['message']} "
        f"({error_details['exception_type']}) "
        f"Status: {error_details['status_code']}"
    )
    if request:
        log_message += f" URL: {request.method} {request.url}"

    logger.log(log_level, log_message)

    # Log detailed error info at debug level
    # Avoid logging potentially sensitive request headers/body in production logs unless necessary
    # Consider filtering sensitive fields if logging full details
    logger.debug(f"Detailed error {error_id}: {json.dumps(error_details, default=str)}") # Use default=str for non-serializable items

    return error_id

def report_exception(exc: Exception, request: Optional[Request] = None) -> None:
    """Report exception to external error tracking service.

    Args:
        exc: Exception object
        request: Optional FastAPI Request object.
    """
    # TODO: Integrate with your chosen error tracking service (e.g., Sentry, Rollbar)
    # Example (conceptual):
    # if SENTRY_DSN:
    #     sentry_sdk.capture_exception(exc)
    # else:
    #     # Fallback logging if no external service configured
    #     error_details = format_exception(exc, request)
    #     print(f"ERROR REPORT (External Service): {json.dumps(error_details, default=str)}")
    pass # Placeholder

# Removed Flask-specific error_response function.
# FastAPI exception handlers create responses directly (e.g., JSONResponse).

# Removed Flask-specific handle_exceptions decorator.
# Use FastAPI's Depends or middleware for pre-request checks,
# and exception handlers for catching errors.

# Removed Flask-specific setup_error_handlers function.
# TODO: Implement exception handlers in your FastAPI application (e.g., in main.py)
# Example:
# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# from .utils.error_handling import AppError, log_exception, report_exception
#
# app = FastAPI()
#
# @app.exception_handler(AppError)
# async def app_exception_handler(request: Request, exc: AppError):
#     log_exception(exc, request)
#     # Optionally report specific AppErrors
#     # report_exception(exc, request)
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={
#             "error": exc.error_code,
#             "message": exc.message,
#             "error_id": exc.error_id,
#             # "details": exc.details # Optionally include details
#         },
#     )
#
# @app.exception_handler(Exception)
# async def generic_exception_handler(request: Request, exc: Exception):
#     # Log and report unexpected errors
#     error_id = log_exception(exc, request, logging.CRITICAL)
#     report_exception(exc, request) # Report all unexpected exceptions
#     return JSONResponse(
#         status_code=500,
#         content={
#             "error": "internal_error",
#             "message": "An unexpected internal server error occurred.",
#             "error_id": error_id,
#         },
#     )
#
# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     # Handle FastAPI's built-in HTTPExceptions
#     # You might want to log these depending on the status code
#     if exc.status_code >= 500:
#          log_exception(exc, request, logging.ERROR)
#          report_exception(exc, request)
#     elif exc.status_code >= 400:
#          log_exception(exc, request, logging.WARNING)
#
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.detail}, # Standard FastAPI detail field
#         headers=getattr(exc, "headers", None),
#     )


# ===== Error Monitoring =====

class ErrorMonitor:
    """Error monitoring and tracking utilities."""

    @staticmethod
    def capture_exception(exc: Exception, request: Optional[Request] = None, context: Optional[Dict[str, Any]] = None) -> str:
        """Capture and report an exception.

        Args:
            exc: Exception object
            request: Optional FastAPI Request object.
            context: Additional context information

        Returns:
            Error ID for reference
        """
        error_details = format_exception(exc, request)

        # Add additional context
        if context:
            error_details['context'] = context

        # Log the error
        error_id = log_exception(exc, request) # Log level determined by log_exception

        # Report to error tracking service
        report_exception(exc, request)

        return error_id

    @staticmethod
    def capture_message(message: str, request: Optional[Request] = None, level: str = 'error',
                       context: Optional[Dict[str, Any]] = None) -> str:
        """Capture and report a message.

        Args:
            message: Message to capture
            request: Optional FastAPI Request object.
            level: Log level (error, warning, info, debug)
            context: Additional context information

        Returns:
            Message ID for reference
        """
        message_id = str(uuid.uuid4())
        log_level_int = getattr(logging, level.upper(), logging.ERROR)

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
                'url': str(request.url),
                'method': request.method,
                'client_host': request.client.host if request.client else None
            }

        # Log the message
        log_func = getattr(logger, level.lower(), logger.error)
        log_func(f"{level.upper()}: {message} (ID: {message_id})")

        # TODO: Integrate with your chosen error tracking service to report messages
        # Example (conceptual):
        # if SENTRY_DSN:
        #     sentry_sdk.capture_message(message, level=level, extra=message_details)
        # else:
        #     print(f"MESSAGE CAPTURE (External Service): {json.dumps(message_details, default=str)}")
        pass # Placeholder

        return message_id

    # Removed Flask-specific monitor decorator.
    # Use try/except blocks with ErrorMonitor.capture_exception directly,
    # or implement custom middleware/dependency for broader monitoring if needed.