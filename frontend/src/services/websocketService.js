import { io } from 'socket.io-client';

// Get backend URL from environment variables (ensure VITE_WS_BASE_URL is set in .env)
// Default to localhost:5000 if not set, assuming backend runs there in dev
const WS_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:5000';

class WebSocketService {
  socket = null;
  messageListeners = new Map(); // Store listeners keyed by event type

  connect(authToken) {
    if (this.socket && this.socket.connected) {
      console.log('WebSocket already connected.');
      return;
    }

    console.log(`Attempting to connect WebSocket to ${WS_URL}`);
    // Pass auth token if needed for connection authentication on the backend
    this.socket = io(WS_URL, {
      // Use 'ws://' or 'wss://' based on your backend setup
      // Consider adding authentication if your backend requires it
      // auth: { token: authToken },
      reconnectionAttempts: 5,
      reconnectionDelay: 3000,
      transports: ['websocket'], // Force websocket transport
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected successfully:', this.socket.id);
      // Potentially emit an event or call a callback for successful connection
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      // Handle disconnection logic (e.g., notify user, attempt reconnect)
      if (reason === 'io server disconnect') {
        // The server intentionally disconnected the socket, probably needs re-authentication
        this.socket.connect();
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      // Handle connection errors (e.g., show error message)
    });

    // Generic handler for registered listeners
    this.socket.onAny((eventName, ...args) => {
      if (this.messageListeners.has(eventName)) {
        this.messageListeners.get(eventName).forEach(callback => {
          try {
            callback(...args);
          } catch (error) {
            console.error(`Error in WebSocket listener for ${eventName}:`, error);
          }
        });
      } else {
         console.log(`Received unhandled WebSocket event: ${eventName}`, args);
      }
    });
  }

  disconnect() {
    if (this.socket) {
      console.log('Disconnecting WebSocket...');
      this.socket.disconnect();
      this.socket = null;
      this.messageListeners.clear(); // Clear listeners on disconnect
    }
  }

  emit(eventName, data) {
    if (this.socket && this.socket.connected) {
      this.socket.emit(eventName, data);
    } else {
      console.error('WebSocket not connected. Cannot emit event:', eventName);
    }
  }

  // Add a listener for a specific event type
  addListener(eventName, callback) {
    if (!this.messageListeners.has(eventName)) {
      this.messageListeners.set(eventName, new Set());
    }
    this.messageListeners.get(eventName).add(callback);
    console.log(`Added listener for WebSocket event: ${eventName}`);
  }

  // Remove a specific listener
  removeListener(eventName, callback) {
    if (this.messageListeners.has(eventName)) {
      this.messageListeners.get(eventName).delete(callback);
      if (this.messageListeners.get(eventName).size === 0) {
        this.messageListeners.delete(eventName);
      }
      console.log(`Removed listener for WebSocket event: ${eventName}`);
    }
  }

  // Remove all listeners for a specific event
  removeAllListeners(eventName) {
     if (this.messageListeners.has(eventName)) {
        this.messageListeners.delete(eventName);
        console.log(`Removed all listeners for WebSocket event: ${eventName}`);
     }
  }

  // Example: Subscribe to updates for a specific task
  subscribeToTask(taskId) {
    this.emit('subscribe_task', { taskId });
    console.log(`Emitted subscribe_task for taskId: ${taskId}`);
  }

  // Example: Unsubscribe from updates for a specific task
  unsubscribeFromTask(taskId) {
    this.emit('unsubscribe_task', { taskId });
     console.log(`Emitted unsubscribe_task for taskId: ${taskId}`);
  }
}

// Export a singleton instance
const websocketService = new WebSocketService();
export default websocketService;