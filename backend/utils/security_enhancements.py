"""
Security enhancements for production deployment.

This module provides advanced security features for the application:
1. Strong encryption using Fernet (symmetric encryption)
2. CSRF protection
3. Input validation utilities
4. Rate limiting
5. Enhanced password policies
6. Security headers configuration
"""

import os
import re
import time
import hashlib
import secrets
import base64
from typing import Dict, Any, Optional, Tuple, List, Union, Callable
from functools import wraps
from datetime import datetime, timedelta

from flask import request, abort, jsonify, Response, g
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from utils.logger import setup_logger

logger = setup_logger('utils.security_enhancements')

# ===== Strong Encryption =====

def generate_encryption_key(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """Generate a Fernet encryption key from a password.
    
    Args:
        password: Password to derive key from
        salt: Optional salt, generated if not provided
        
    Returns:
        Tuple of (key, salt)
    """
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def get_encryption_key() -> bytes:
    """Get or create the application encryption key.
    
    Returns:
        Fernet encryption key
    """
    env_key = os.environ.get('ENCRYPTION_KEY')
    
    if env_key:
        # Use environment variable if available
        try:
            # Ensure the key is valid base64
            return base64.urlsafe_b64encode(base64.urlsafe_b64decode(env_key.encode()))
        except Exception as e:
            logger.error(f"Invalid ENCRYPTION_KEY format: {e}")
    
    # Fallback to derived key
    password = os.environ.get('SECRET_KEY', 'change-this-in-production')
    key, _ = generate_encryption_key(password)
    return key

def encrypt_data(data: Union[str, bytes, dict]) -> str:
    """Encrypt data using Fernet symmetric encryption.
    
    Args:
        data: Data to encrypt (string, bytes, or dict)
        
    Returns:
        Base64-encoded encrypted data
    """
    key = get_encryption_key()
    f = Fernet(key)
    
    # Convert data to bytes
    if isinstance(data, dict):
        data_bytes = str(data).encode()
    elif isinstance(data, str):
        data_bytes = data.encode()
    else:
        data_bytes = data
    
    # Encrypt
    encrypted = f.encrypt(data_bytes)
    return base64.urlsafe_b64encode(encrypted).decode()

def decrypt_data(encrypted_data: str) -> bytes:
    """Decrypt Fernet-encrypted data.
    
    Args:
        encrypted_data: Base64-encoded encrypted data
        
    Returns:
        Decrypted data as bytes
    """
    key = get_encryption_key()
    f = Fernet(key)
    
    try:
        # Decode base64 and decrypt
        decoded = base64.urlsafe_b64decode(encrypted_data.encode())
        return f.decrypt(decoded)
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise ValueError("Failed to decrypt data")

# ===== CSRF Protection =====

def generate_csrf_token() -> str:
    """Generate a secure CSRF token.
    
    Returns:
        CSRF token string
    """
    return secrets.token_hex(32)

def validate_csrf_token(token: str) -> bool:
    """Validate a CSRF token against the session token.
    
    Args:
        token: CSRF token to validate
        
    Returns:
        True if valid, False otherwise
    """
    # In a real implementation, compare with token stored in session
    session_token = request.cookies.get('csrf_token')
    return session_token is not None and token == session_token

def csrf_protect(f):
    """Decorator to protect routes against CSRF attacks."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip for GET, HEAD, OPTIONS, TRACE
        if request.method in ['GET', 'HEAD', 'OPTIONS', 'TRACE']:
            return f(*args, **kwargs)
        
        # Check CSRF token in header or form
        token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        
        if not token or not validate_csrf_token(token):
            logger.warning(f"CSRF validation failed for {request.path}")
            abort(403, description="CSRF validation failed")
            
        return f(*args, **kwargs)
    return decorated_function

# ===== Input Validation =====

class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if len(password) < 12:
            return False, "Password must be at least 12 characters long"
        
        checks = [
            (r'[A-Z]', "at least one uppercase letter"),
            (r'[a-z]', "at least one lowercase letter"),
            (r'[0-9]', "at least one number"),
            (r'[^A-Za-z0-9]', "at least one special character")
        ]
        
        failed = [msg for pattern, msg in checks if not re.search(pattern, password)]
        
        if failed:
            return False, f"Password must contain {', '.join(failed)}"
        
        return True, "Password meets strength requirements"
    
    @staticmethod
    def sanitize_string(input_str: str) -> str:
        """Sanitize a string for safe display/storage.
        
        Args:
            input_str: String to sanitize
            
        Returns:
            Sanitized string
        """
        # Remove potentially dangerous characters
        return re.sub(r'[<>&"/\']', '', input_str)
    
    @staticmethod
    def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate JSON data against a schema.
        
        Args:
            data: JSON data to validate
            schema: Schema definition
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Simple schema validation
        for field, field_schema in schema.items():
            # Check required fields
            if field_schema.get('required', False) and field not in data:
                return False, f"Missing required field: {field}"
            
            # Skip validation if field is not present
            if field not in data:
                continue
                
            value = data[field]
            
            # Type validation
            expected_type = field_schema.get('type')
            if expected_type:
                if expected_type == 'string' and not isinstance(value, str):
                    return False, f"Field {field} must be a string"
                elif expected_type == 'number' and not isinstance(value, (int, float)):
                    return False, f"Field {field} must be a number"
                elif expected_type == 'boolean' and not isinstance(value, bool):
                    return False, f"Field {field} must be a boolean"
                elif expected_type == 'array' and not isinstance(value, list):
                    return False, f"Field {field} must be an array"
                elif expected_type == 'object' and not isinstance(value, dict):
                    return False, f"Field {field} must be an object"
            
            # Pattern validation for strings
            if isinstance(value, str) and 'pattern' in field_schema:
                pattern = field_schema['pattern']
                if not re.match(pattern, value):
                    return False, f"Field {field} does not match required pattern"
            
            # Min/max validation for strings and arrays
            if isinstance(value, (str, list)):
                if 'minLength' in field_schema and len(value) < field_schema['minLength']:
                    return False, f"Field {field} must be at least {field_schema['minLength']} characters long"
                if 'maxLength' in field_schema and len(value) > field_schema['maxLength']:
                    return False, f"Field {field} must be at most {field_schema['maxLength']} characters long"
            
            # Min/max validation for numbers
            if isinstance(value, (int, float)):
                if 'minimum' in field_schema and value < field_schema['minimum']:
                    return False, f"Field {field} must be at least {field_schema['minimum']}"
                if 'maximum' in field_schema and value > field_schema['maximum']:
                    return False, f"Field {field} must be at most {field_schema['maximum']}"
        
        return True, None

# ===== Rate Limiting =====

class RateLimiter:
    """Rate limiting implementation."""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        """Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_records = {}  # IP -> list of timestamps
    
    def is_rate_limited(self, ip_address: str) -> bool:
        """Check if a request should be rate limited.
        
        Args:
            ip_address: Client IP address
            
        Returns:
            True if rate limited, False otherwise
        """
        current_time = time.time()
        
        # Initialize record for new IP
        if ip_address not in self.request_records:
            self.request_records[ip_address] = []
        
        # Clean up old records
        self.request_records[ip_address] = [
            timestamp for timestamp in self.request_records[ip_address]
            if current_time - timestamp < self.time_window
        ]
        
        # Check rate limit
        if len(self.request_records[ip_address]) >= self.max_requests:
            return True
        
        # Record this request
        self.request_records[ip_address].append(current_time)
        return False

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(f):
    """Decorator to apply rate limiting to routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        if rate_limiter.is_rate_limited(ip_address):
            logger.warning(f"Rate limit exceeded for IP: {ip_address}")
            response = jsonify({
                'error': 'Rate limit exceeded',
                'status': 429,
                'message': 'Too many requests, please try again later'
            })
            response.status_code = 429
            return response
            
        return f(*args, **kwargs)
    return decorated_function

# ===== Enhanced JWT Handling =====

def generate_token_pair(user_id: str, email: str) -> Dict[str, str]:
    """Generate access and refresh token pair.
    
    Args:
        user_id: User ID
        email: User email
        
    Returns:
        Dict with access_token and refresh_token
    """
    secret_key = os.environ.get('JWT_SECRET_KEY', 'change-this-in-production')
    
    # Access token - short lived
    access_expiration = datetime.utcnow() + timedelta(minutes=15)
    access_payload = {
        'user_id': user_id,
        'email': email,
        'exp': access_expiration,
        'type': 'access'
    }
    access_token = jwt.encode(access_payload, secret_key, algorithm='HS256')
    
    # Refresh token - longer lived
    refresh_expiration = datetime.utcnow() + timedelta(days=7)
    refresh_payload = {
        'user_id': user_id,
        'email': email,
        'exp': refresh_expiration,
        'type': 'refresh'
    }
    refresh_token = jwt.encode(refresh_payload, secret_key, algorithm='HS256')
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

def verify_and_refresh_token(refresh_token: str) -> Optional[Dict[str, str]]:
    """Verify a refresh token and generate a new token pair.
    
    Args:
        refresh_token: Refresh token to verify
        
    Returns:
        New token pair or None if invalid
    """
    secret_key = os.environ.get('JWT_SECRET_KEY', 'change-this-in-production')
    
    try:
        payload = jwt.decode(refresh_token, secret_key, algorithms=['HS256'])
        
        # Ensure it's a refresh token
        if payload.get('type') != 'refresh':
            logger.warning("Token type is not refresh")
            return None
        
        # Generate new token pair
        return generate_token_pair(payload['user_id'], payload['email'])
    except jwt.ExpiredSignatureError:
        logger.warning("Refresh token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid refresh token: {e}")
        return None

def jwt_required(f):
    """Decorator to require valid JWT for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("Missing or invalid Authorization header")
            return jsonify({
                'error': 'Authorization required',
                'status': 401
            }), 401
        
        token = auth_header.split(' ')[1]
        secret_key = os.environ.get('JWT_SECRET_KEY', 'change-this-in-production')
        
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Ensure it's an access token
            if payload.get('type') != 'access':
                logger.warning("Token type is not access")
                return jsonify({
                    'error': 'Invalid token type',
                    'status': 401
                }), 401
            
            # Store user info in Flask g object for route handlers
            g.user_id = payload['user_id']
            g.email = payload['email']
            
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return jsonify({
                'error': 'Token expired',
                'status': 401,
                'code': 'token_expired'  # Special code for frontend to handle refresh
            }), 401
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return jsonify({
                'error': 'Invalid token',
                'status': 401
            }), 401
    
    return decorated_function

# ===== Enhanced Security Headers =====

def enhanced_security_headers(response):
    """Apply enhanced security headers to response.
    
    Args:
        response: Flask response object
        
    Returns:
        Modified response with security headers
    """
    # HTTPS enforcement
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    
    # Content security policy - customize based on your needs
    csp_directives = [
        "default-src 'self'",
        "script-src 'self' https://apis.google.com https://js.stripe.com",
        "connect-src 'self' https://api.stripe.com",
        "img-src 'self' data: https://www.gstatic.com",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
        "font-src 'self' https://fonts.gstatic.com",
        "frame-src 'self' https://js.stripe.com https://accounts.google.com",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "frame-ancestors 'none'",
        "upgrade-insecure-requests"
    ]
    response.headers['Content-Security-Policy'] = "; ".join(csp_directives)
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Enable browser XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Control referrer information
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions policy (formerly Feature-Policy)
    permissions = [
        "geolocation=()",
        "microphone=()",
        "camera=()",
        "payment=(self)",
        "usb=()"
    ]
    response.headers['Permissions-Policy'] = ", ".join(permissions)
    
    return response