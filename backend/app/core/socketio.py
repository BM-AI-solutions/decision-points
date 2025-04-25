"""
Socket.IO server initialization.
This module initializes the Socket.IO server to be used throughout the application.
"""
import socketio
import logging

logger = logging.getLogger(__name__)

# Initialize Socket.IO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')  # Adjust cors_allowed_origins for production

# Basic Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    logger.info(f"Socket.IO client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"Socket.IO client disconnected: {sid}")
