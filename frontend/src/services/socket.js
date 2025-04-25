/**
 * Socket.IO service for real-time communication with the backend.
 * Handles agent updates and task status changes.
 */

import { io } from 'socket.io-client';

// Get API base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// Create a Socket.IO instance
const socket = io(API_BASE_URL, {
  autoConnect: false,
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  timeout: 20000,
});

// Event listeners
const eventListeners = {
  connect: [],
  disconnect: [],
  agent_update: [],
  error: [],
};

// Socket event handlers
socket.on('connect', () => {
  console.log('Socket connected');
  eventListeners.connect.forEach(callback => callback());
});

socket.on('disconnect', (reason) => {
  console.log(`Socket disconnected: ${reason}`);
  eventListeners.disconnect.forEach(callback => callback(reason));
});

socket.on('agent_update', (data) => {
  console.log('Agent update received:', data);
  eventListeners.agent_update.forEach(callback => callback(data));
});

socket.on('error', (error) => {
  console.error('Socket error:', error);
  eventListeners.error.forEach(callback => callback(error));
});

/**
 * Socket service for real-time communication with the backend.
 */
const socketService = {
  /**
   * Connect to the Socket.IO server.
   */
  connect() {
    if (!socket.connected) {
      socket.connect();
    }
  },

  /**
   * Disconnect from the Socket.IO server.
   */
  disconnect() {
    if (socket.connected) {
      socket.disconnect();
    }
  },

  /**
   * Join a task room to receive updates for a specific task.
   *
   * @param {string} taskId - The ID of the task to join.
   * @returns {Promise<boolean>} - A promise that resolves to true if the join was successful.
   */
  joinTask(taskId) {
    return new Promise((resolve, reject) => {
      socket.emit('join_task', { task_id: taskId }, (response) => {
        if (response && response.success) {
          console.log(`Joined task room: ${taskId}`);
          resolve(true);
        } else {
          console.error(`Failed to join task room: ${taskId}`, response);
          reject(new Error(response?.error || 'Failed to join task room'));
        }
      });
    });
  },

  /**
   * Leave a task room to stop receiving updates for a specific task.
   *
   * @param {string} taskId - The ID of the task to leave.
   * @returns {Promise<boolean>} - A promise that resolves to true if the leave was successful.
   */
  leaveTask(taskId) {
    return new Promise((resolve, reject) => {
      socket.emit('leave_task', { task_id: taskId }, (response) => {
        if (response && response.success) {
          console.log(`Left task room: ${taskId}`);
          resolve(true);
        } else {
          console.error(`Failed to leave task room: ${taskId}`, response);
          reject(new Error(response?.error || 'Failed to leave task room'));
        }
      });
    });
  },

  /**
   * Add an event listener for a specific event.
   *
   * @param {string} event - The event to listen for ('connect', 'disconnect', 'agent_update', 'error').
   * @param {Function} callback - The callback function to call when the event occurs.
   */
  on(event, callback) {
    if (eventListeners[event]) {
      eventListeners[event].push(callback);
    } else {
      console.warn(`Unknown event: ${event}`);
    }
  },

  /**
   * Remove an event listener for a specific event.
   *
   * @param {string} event - The event to stop listening for.
   * @param {Function} callback - The callback function to remove.
   */
  off(event, callback) {
    if (eventListeners[event]) {
      const index = eventListeners[event].indexOf(callback);
      if (index !== -1) {
        eventListeners[event].splice(index, 1);
      }
    } else {
      console.warn(`Unknown event: ${event}`);
    }
  },

  /**
   * Check if the socket is connected.
   *
   * @returns {boolean} - True if the socket is connected, false otherwise.
   */
  isConnected() {
    return socket.connected;
  },
};

export default socketService;
