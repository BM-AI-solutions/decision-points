"""
Socket.IO server initialization and WebSocket manager for A2A protocol.
This module initializes the Socket.IO server and provides a WebSocket manager
for real-time updates from agents using the A2A protocol.
"""
import asyncio
import socketio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Initialize Socket.IO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')  # Adjust cors_allowed_origins for production

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    logger.info(f"Socket.IO client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"Socket.IO client disconnected: {sid}")

@sio.event
async def join_task(sid, data):
    """
    Handle a client joining a task room.

    Args:
        sid: The session ID of the client.
        data: The data containing the task ID to join.
    """
    if not isinstance(data, dict) or 'task_id' not in data:
        logger.warning(f"Invalid join_task data from client {sid}: {data}")
        return {'success': False, 'error': 'Invalid data format. Expected {task_id: string}'}

    task_id = data['task_id']
    logger.info(f"Client {sid} joining task room: {task_id}")

    await sio.enter_room(sid, task_id)

    # Send a welcome message to the client
    await sio.emit('agent_update', {
        'type': 'join',
        'message': f"Joined task room: {task_id}",
        'task_id': task_id,
        'timestamp': asyncio.get_event_loop().time()
    }, room=sid)

    return {'success': True, 'message': f"Joined task room: {task_id}"}

@sio.event
async def leave_task(sid, data):
    """
    Handle a client leaving a task room.

    Args:
        sid: The session ID of the client.
        data: The data containing the task ID to leave.
    """
    if not isinstance(data, dict) or 'task_id' not in data:
        logger.warning(f"Invalid leave_task data from client {sid}: {data}")
        return {'success': False, 'error': 'Invalid data format. Expected {task_id: string}'}

    task_id = data['task_id']
    logger.info(f"Client {sid} leaving task room: {task_id}")

    await sio.leave_room(sid, task_id)

    # Send a confirmation message to the client
    await sio.emit('agent_update', {
        'type': 'leave',
        'message': f"Left task room: {task_id}",
        'task_id': task_id,
        'timestamp': asyncio.get_event_loop().time()
    }, room=sid)

    return {'success': True, 'message': f"Left task room: {task_id}"}

# WebSocket manager for A2A protocol
class WebSocketManager:
    """
    WebSocket manager for A2A protocol.

    This class provides methods for sending real-time updates to clients
    using Socket.IO, with support for A2A protocol events.
    """

    def __init__(self, sio_instance: socketio.AsyncServer):
        """
        Initialize the WebSocket manager.

        Args:
            sio_instance: The Socket.IO server instance.
        """
        self.sio = sio_instance
        logger.info("WebSocket manager initialized")

    async def broadcast(self, room: str, data: Dict[str, Any]) -> bool:
        """
        Broadcast a message to a room.

        Args:
            room: The room to broadcast to (usually a task ID).
            data: The data to broadcast.

        Returns:
            True if the message was sent, False otherwise.
        """
        try:
            await self.sio.emit('agent_update', data, room=room)
            logger.debug(f"Broadcast message to room {room}: {data}")
            return True
        except Exception as e:
            logger.error(f"Error broadcasting message to room {room}: {e}", exc_info=True)
            return False

    async def broadcast_agent_event(
        self,
        task_id: str,
        agent_name: str,
        event_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Broadcast an agent event to a room.

        Args:
            task_id: The task ID (room) to broadcast to.
            agent_name: The name of the agent sending the event.
            event_type: The type of event (e.g., 'start', 'progress', 'complete', 'error').
            message: The message to display to the user.
            data: Optional additional data to include in the event.

        Returns:
            True if the event was sent, False otherwise.
        """
        event_data = {
            'agent': agent_name,
            'type': event_type,
            'message': message,
            'timestamp': asyncio.get_event_loop().time(),
        }

        if data:
            event_data.update(data)

        return await self.broadcast(task_id, event_data)

    async def join_room(self, sid: str, room: str) -> bool:
        """
        Add a client to a room.

        Args:
            sid: The session ID of the client.
            room: The room to join.

        Returns:
            True if the client joined the room, False otherwise.
        """
        try:
            await self.sio.enter_room(sid, room)
            logger.debug(f"Client {sid} joined room {room}")
            return True
        except Exception as e:
            logger.error(f"Error adding client {sid} to room {room}: {e}", exc_info=True)
            return False

    async def leave_room(self, sid: str, room: str) -> bool:
        """
        Remove a client from a room.

        Args:
            sid: The session ID of the client.
            room: The room to leave.

        Returns:
            True if the client left the room, False otherwise.
        """
        try:
            await self.sio.leave_room(sid, room)
            logger.debug(f"Client {sid} left room {room}")
            return True
        except Exception as e:
            logger.error(f"Error removing client {sid} from room {room}: {e}", exc_info=True)
            return False

# Create a singleton instance of the WebSocket manager
websocket_manager = WebSocketManager(sio)
