from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an asynchronous database session per request.

    Ensures the session is closed even if errors occur.
    """
    async with SessionLocal() as session:
        try:
            yield session
            # Optional: await session.commit() # If you want auto-commit, though often handled in services/repos
        except Exception:
            await session.rollback() # Rollback on error
            raise
        finally:
            # The 'async with SessionLocal() as session:' context manager
            # handles closing the session automatically here.
            # Explicit close is not strictly needed but doesn't hurt.
            await session.close()
from aiokafka import AIOKafkaProducer
from backend.app.core.messaging import get_kafka_producer as get_kafka_producer_instance

async def get_kafka_producer() -> AIOKafkaProducer:
    """
    FastAPI dependency that provides the initialized Kafka producer instance.

    Relies on the producer being initialized during application startup via lifespan events.
    """
    # The actual producer instance is retrieved from the messaging module
    # where it's managed as a global variable initialized during lifespan startup.
    return await get_kafka_producer_instance()
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError # Although verify_access_token handles it, good practice to have it if refining error handling

from backend.app import crud, models, schemas # Import top-level packages
from backend.app.core import security
from backend.app.config import settings

# Define the OAuth2 scheme
# tokenUrl should point to the login endpoint we created
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    """
    Dependency to get the current authenticated user based on the JWT token.

    Verifies the token, extracts the user identifier (email), and fetches
    the user from the database.

    Raises:
        HTTPException(401): If the token is invalid, expired, malformed, or the
                           user identified by the token does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    email = security.verify_access_token(token)
    if email is None:
        raise credentials_exception
        
    user = await crud.user.get_user_by_email(db, email=email)
    if user is None:
        # User identified in a valid token doesn't exist anymore
        raise credentials_exception 
        # Alternatively, could raise 404, but 401 might be safer 
        # as it doesn't reveal if the email was ever valid.
        
    # TODO: Add check for user active status if needed:
    # if not user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
        
    return user