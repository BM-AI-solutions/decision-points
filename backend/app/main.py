import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging_config import setup_logging
from app.config import settings
from app.core.db import Base, engine, SessionLocal
from app.models.user import User  # Import model to ensure it's registered with Base
from app.core.messaging import (
    start_kafka_producer,
    stop_kafka_producer,
    start_kafka_consumer,
    stop_kafka_consumer,
)
from app.core.socketio import sio  # Import the Socket.IO server from the core module

# Apply logging configuration
setup_logging()

# Get logger after configuration is applied
logger = logging.getLogger("app") # Use 'app' logger defined in config
# Configure logging basic setup (adjust as needed)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan events:
    - Create database tables on startup.
    - Start Kafka producer and consumer on startup (if enabled).
    - Stop Kafka consumer and producer on shutdown (if enabled).
    """
    # Startup: Initialize DB tables
    logger.info("Lifespan: Initializing database...")
    async with engine.begin() as conn:
        # Create tables if they don't exist (for local development)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Lifespan: Database tables checked/created.")

    # Check if Kafka is disabled
    kafka_disabled = os.environ.get('DISABLE_KAFKA', '').lower() in ('true', '1', 'yes')

    if not kafka_disabled:
        # Startup: Initialize Kafka clients
        logger.info("Lifespan: Starting Kafka clients...")
        await start_kafka_producer()
        await start_kafka_consumer()
        logger.info("Lifespan: Kafka clients startup process initiated.")
    else:
        logger.info("Lifespan: Kafka clients disabled by configuration.")

    yield  # Application runs here

    if not kafka_disabled:
        # Shutdown: Stop Kafka clients
        logger.info("Lifespan: Shutting down Kafka clients...")
        await stop_kafka_consumer() # Stop consumer first
        await stop_kafka_producer()
        logger.info("Lifespan: Kafka clients shutdown complete.")


# Initialize FastAPI app with lifespan manager
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    # Add other FastAPI parameters like version, description etc. if needed
)

# Import the API router after app is created to avoid circular imports
from app.api.v1.api import api_router

# Create Socket.IO ASGI app with FastAPI app
from socketio import ASGIApp
sio_app = ASGIApp(sio, other_asgi_app=app) # Wrap FastAPI app


# --- Exception Handlers ---

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handles any unexpected exceptions that occur during request processing.

    Logs the full exception and returns a standardized 500 Internal Server Error
    response to avoid leaking sensitive details.
    """
    logger.error(f"Unhandled exception for request {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )

# Note: You can add more specific handlers here if needed, e.g.:
# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     # You could add custom logging or formatting for HTTPExceptions here
#     # For now, we let FastAPI handle its own HTTPExceptions by default
#     # return JSONResponse(
#     #     status_code=exc.status_code,
#     #     content={"detail": exc.detail},
#     #     headers=exc.headers,
#     # )
#     # Re-raising or letting FastAPI handle it implicitly might be simpler:
#     pass # Let FastAPI handle default HTTPException behavior

# @app.exception_handler(YourCustomError)
# async def custom_error_handler(request: Request, exc: YourCustomError):
#     # Handle your specific custom application errors
#     pass

# --- End Exception Handlers ---

# Include the API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Root endpoint (optional, can be useful for basic checks)
@app.get("/", tags=["root"])
async def read_root():
    """
    Root endpoint providing basic application information.
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


# If running directly using `python backend/app/main.py` (for simple testing)
# Note: Uvicorn is the recommended way to run in development and production.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        reload=settings.UVICORN_RELOAD,
    )
