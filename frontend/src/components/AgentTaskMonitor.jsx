import React, { useState, useEffect } from 'react';
import AgentUpdates from './AgentUpdates';
import api from '../services/api';
import socketService from '../services/socket';

/**
 * Component to monitor and display agent task progress.
 * 
 * @param {Object} props - Component props
 * @param {string} props.initialPrompt - The initial prompt to send to the agents
 * @param {Function} props.onComplete - Callback function to call when the task is complete
 * @param {Function} props.onError - Callback function to call when an error occurs
 */
const AgentTaskMonitor = ({ initialPrompt, onComplete, onError }) => {
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, loading, complete, error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Start the task when the component mounts
  useEffect(() => {
    if (initialPrompt && status === 'idle') {
      startTask();
    }
  }, [initialPrompt]);

  // Connect to the socket when the component mounts
  useEffect(() => {
    socketService.connect();

    return () => {
      socketService.disconnect();
    };
  }, []);

  // Start a new task
  const startTask = async () => {
    try {
      setStatus('loading');
      setError(null);
      setResult(null);

      // Call the orchestration API
      const response = await api.orchestrateAgents(initialPrompt);
      
      // Set the task ID
      setTaskId(response.data.task_id);
      
      // Listen for task completion
      socketService.on('agent_update', handleAgentUpdate);
    } catch (err) {
      console.error('Failed to start task:', err);
      setStatus('error');
      setError(err.message || 'Failed to start task');
      if (onError) onError(err);
    }
  };

  // Handle agent updates
  const handleAgentUpdate = (data) => {
    console.log('Agent update:', data);
    
    // Check if the update is for the current task
    if (data.task_id !== taskId) return;
    
    // Check if the task is complete
    if (data.status === 'completed') {
      setStatus('complete');
      setResult(data.result);
      
      // Remove the event listener
      socketService.off('agent_update', handleAgentUpdate);
      
      // Call the onComplete callback
      if (onComplete) onComplete(data.result);
    }
    
    // Check if the task failed
    if (data.status === 'failed') {
      setStatus('error');
      setError(data.message || 'Task failed');
      
      // Remove the event listener
      socketService.off('agent_update', handleAgentUpdate);
      
      // Call the onError callback
      if (onError) onError(new Error(data.message || 'Task failed'));
    }
  };

  return (
    <div className="agent-task-monitor">
      <div className="task-header">
        <h3>Agent Task Monitor</h3>
        <div className={`task-status ${status}`}>
          {status === 'idle' && 'Ready'}
          {status === 'loading' && 'Processing...'}
          {status === 'complete' && 'Complete'}
          {status === 'error' && 'Error'}
        </div>
      </div>

      {status === 'error' && (
        <div className="task-error">
          <p>Error: {error}</p>
          <button className="btn btn-primary" onClick={startTask}>
            Retry
          </button>
        </div>
      )}

      {taskId && (
        <div className="task-content">
          <div className="task-info">
            <div className="task-id">Task ID: {taskId}</div>
            <div className="task-prompt">Prompt: {initialPrompt}</div>
          </div>

          <AgentUpdates taskId={taskId} autoConnect={false} />

          {status === 'complete' && result && (
            <div className="task-result">
              <h4>Result:</h4>
              <pre>{typeof result === 'string' ? result : JSON.stringify(result, null, 2)}</pre>
            </div>
          )}
        </div>
      )}

      {status === 'idle' && (
        <div className="task-start">
          <p>Enter a prompt to start a new task.</p>
          <button className="btn btn-primary" onClick={startTask} disabled={!initialPrompt}>
            Start Task
          </button>
        </div>
      )}
    </div>
  );
};

export default AgentTaskMonitor;
