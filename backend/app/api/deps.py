from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from .core.db import SessionLocal

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
from .core.messaging import get_kafka_producer as get_kafka_producer_instance

async def get_kafka_producer() -> AIOKafkaProducer:
    """
    FastAPI dependency that provides the initialized Kafka producer instance.

    Relies on the producer being initialized during application startup via lifespan events.
    """
    # The actual producer instance is retrieved from the messaging module
    # where it's managed as a global variable initialized during lifespan startup.
    return await get_kafka_producer_instance()
from fastapi import Depends # Removed HTTPException, status

# Authentication dependencies removed.