import os
import jwt
import secrets
import hashlib
import base64
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

from utils.logger import setup_logger

logger = setup_logger('utils.security')

def generate_token(user_id: str, email: str, expiration_hours: int = 24) -> str:
    """Generate a JWT token for a user.

    Args:
        user_id: User ID
        email: User email
        expiration_hours: Token expiration time in hours

    Returns:
        JWT token
    """
    secret_key = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
    expiration = datetime.utcnow() + timedelta(hours=expiration_hours)

    payload = {
        'user_id': user_id,
        'email': email,
        'exp': expiration
    }

    logger.debug(f"Generating token for user {user_id}")
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token.

    Args:
        token: JWT token to verify

    Returns:
        Token payload if valid, None otherwise
    """
    secret_key = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')

    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        logger.debug(f"Token verified for user {payload.get('user_id')}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return None

def hash_password(password: str) -> str:
    """Hash a password using Werkzeug's generate_password_hash.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return generate_password_hash(password)

def verify_password(hashed_password: str, password: str) -> bool:
    """Verify a password against its hash using Werkzeug's check_password_hash.

    Args:
        hashed_password: Hashed password
        password: Plain text password to check

    Returns:
        True if password matches, False otherwise
    """
    return check_password_hash(hashed_password, password)

def generate_api_key() -> Tuple[str, str]:
    """Generate a secure API key and its hash.

    Returns:
        Tuple of (API key, hashed API key)
    """
    # Generate a secure random API key
    api_key = secrets.token_hex(32)

    # Hash the API key for storage
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    logger.debug("Generated new API key")
    return api_key, api_key_hash

def verify_api_key(api_key: str, hashed_api_key: str) -> bool:
    """Verify an API key against its hash.

    Args:
        api_key: API key to verify
        hashed_api_key: Hashed API key

    Returns:
        True if API key matches, False otherwise
    """
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return api_key_hash == hashed_api_key

def encrypt_data(data: str, key: Optional[str] = None) -> str:
    """Encrypt sensitive data.

    Args:
        data: Data to encrypt
        key: Encryption key (uses env var ENCRYPTION_KEY if None)

    Returns:
        Encrypted data as base64 string
    """
    # For demonstration purposes, this is a simplified encryption.
    # In a production environment, use a proper encryption library.
    if key is None:
        key = os.environ.get('ENCRYPTION_KEY', 'dev-encryption-key-change-in-production')

    # XOR encryption (simple, not for production use)
    encrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))
    return base64.b64encode(encrypted.encode()).decode()

def decrypt_data(encrypted_data: str, key: Optional[str] = None) -> str:
    """Decrypt sensitive data.

    Args:
        encrypted_data: Encrypted data as base64 string
        key: Encryption key (uses env var ENCRYPTION_KEY if None)

    Returns:
        Decrypted data
    """
    # For demonstration purposes, this is a simplified decryption.
    # In a production environment, use a proper encryption library.
    if key is None:
        key = os.environ.get('ENCRYPTION_KEY', 'dev-encryption-key-change-in-production')

    # XOR decryption (simple, not for production use)
    encrypted = base64.b64decode(encrypted_data).decode()
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(encrypted))