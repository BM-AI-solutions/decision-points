from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.config import settings

# Create the async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True, # Recommended for checking connections before use
    # echo=True # Uncomment for debugging SQL statements
)

# Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession, # Use AsyncSession for async operations
    expire_on_commit=False # Recommended for FastAPI background tasks
)

# Base class for declarative models
Base = declarative_base()