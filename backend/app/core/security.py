from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Initialize the password context
# Using bcrypt as the default hashing algorithm
# Deprecated algorithms can be listed if needed for migrating old hashes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta | None = None
) -> str:
    """
    Creates a JWT access token.

    Args:
        subject: The subject of the token (e.g., user ID or email).
        expires_delta: Optional timedelta for token expiry. Defaults to
                       ACCESS_TOKEN_EXPIRE_MINUTES from settings.

    Returns:
        The encoded JWT access token.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> str | None:
    """
    Verifies the JWT access token and returns the subject (user identifier).

    Args:
        token: The JWT token string.

    Returns:
        The subject (user identifier) from the token payload if verification
        is successful, otherwise None. Returns None if token is invalid,
        expired, or has an invalid signature.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject: str | None = payload.get("sub")
        if subject is None:
            # Token is valid but doesn't contain a subject
            return None
        # Optionally add more checks here, e.g., token type, issuer
        return subject
    except JWTError:
        # Covers invalid signature, expired token, invalid format etc.
        return None