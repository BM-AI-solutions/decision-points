import React, { useState, useEffect } from 'react';
import socketService from '../services/socket';

/**
 * Component to display real-time agent updates for a specific task.
 * 
 * @param {Object} props - Component props
 * @param {string} props.taskId - The ID of the task to display updates for
 * @param {boolean} props.autoConnect - Whether to automatically connect to the socket
 */
const AgentUpdates = ({ taskId, autoConnect = true }) => {
  const [updates, setUpdates] = useState([]);
  const [connected, setConnected] = useState(false);

  // Connect to the socket when the component mounts
  useEffect(() => {
    if (autoConnect) {
      socketService.connect();
    }

    // Set up event listeners
    const handleConnect = () => {
      setConnected(true);
      if (taskId) {
        socketService.joinTask(taskId).catch(error => {
          console.error(`Failed to join task ${taskId}:`, error);
        });
      }
    };

    const handleDisconnect = (reason) => {
      setConnected(false);
      console.log(`Socket disconnected: ${reason}`);
    };

    const handleAgentUpdate = (data) => {
      setUpdates(prevUpdates => [...prevUpdates, {
        id: Date.now(),
        timestamp: new Date(),
        ...data
      }]);
    };

    // Add event listeners
    socketService.on('connect', handleConnect);
    socketService.on('disconnect', handleDisconnect);
    socketService.on('agent_update', handleAgentUpdate);

    // Check if already connected
    if (socketService.isConnected()) {
      handleConnect();
    }

    // Clean up event listeners when the component unmounts
    return () => {
      socketService.off('connect', handleConnect);
      socketService.off('disconnect', handleDisconnect);
      socketService.off('agent_update', handleAgentUpdate);

      // Leave the task room if connected
      if (socketService.isConnected() && taskId) {
        socketService.leaveTask(taskId).catch(error => {
          console.error(`Failed to leave task ${taskId}:`, error);
        });
      }
    };
  }, [taskId, autoConnect]);

  // Join a new task room when the taskId changes
  useEffect(() => {
    if (connected && taskId) {
      socketService.joinTask(taskId).catch(error => {
        console.error(`Failed to join task ${taskId}:`, error);
      });
    }

    // Clean up previous task room
    return () => {
      if (connected && taskId) {
        socketService.leaveTask(taskId).catch(error => {
          console.error(`Failed to leave task ${taskId}:`, error);
        });
      }
    };
  }, [taskId, connected]);

  // Render the updates
  return (
    <div className="agent-updates">
      <div className="agent-updates-header">
        <h3>Agent Updates</h3>
        <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
          {connected ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      {updates.length === 0 ? (
        <div className="no-updates">No updates yet</div>
      ) : (
        <div className="updates-list">
          {updates.map(update => (
            <div key={update.id} className={`update-item ${update.type || 'info'}`}>
              <div className="update-header">
                <span className="agent-name">{update.agent || 'System'}</span>
                <span className="update-time">
                  {update.timestamp.toLocaleTimeString()}
                </span>
              </div>
              <div className="update-message">{update.message}</div>
              {update.result && (
                <div className="update-result">
                  <pre>{typeof update.result === 'string' ? update.result : JSON.stringify(update.result, null, 2)}</pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AgentUpdates;
