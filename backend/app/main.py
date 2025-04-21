import logging
from contextlib import asynccontextmanager
import socketio

from fastapi import FastAPI
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from backend.app.core.logging_config import setup_logging
from backend.app.config import settings
from backend.app.api.v1.api import api_router
from backend.app.core.db import Base, engine
from backend.app.models.user import User  # Import model to ensure it's registered with Base
from backend.app.core.messaging import (
    start_kafka_producer,
    stop_kafka_producer,
    start_kafka_consumer,
    stop_kafka_consumer,
)

# Apply logging configuration
setup_logging()

# Get logger after configuration is applied
logger = logging.getLogger("app") # Use 'app' logger defined in config
# Configure logging basic setup (adjust as needed)

# Initialize Socket.IO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*') # Adjust cors_allowed_origins for production
sio_app = socketio.ASGIApp(sio, other_asgi_app=app) # Wrap FastAPI app



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan events:
    - Create database tables on startup.
    - Start Kafka producer and consumer on startup.
    - Stop Kafka consumer and producer on shutdown.
    """
    # Startup: Initialize DB tables
    logger.info("Lifespan: Initializing database...")
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Optional: Uncomment to drop tables first
        # await conn.run_sync(Base.metadata.create_all) # Removed: Alembic handles migrations
        pass
    logger.info("Lifespan: Database tables checked/created.")

    # Startup: Initialize Kafka clients
    logger.info("Lifespan: Starting Kafka clients...")
    await start_kafka_producer()
    await start_kafka_consumer()
    logger.info("Lifespan: Kafka clients startup process initiated.")

    yield  # Application runs here

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