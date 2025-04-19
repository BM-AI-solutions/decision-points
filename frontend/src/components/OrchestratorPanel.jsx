import React, { useState, useEffect, useCallback } from 'react';
import apiService from '../services/api';
import websocketService from '../services/websocketService';

const OrchestratorPanel = () => {
  // State specifically for the initial topic
  const [initialTopic, setInitialTopic] = useState('');
  const [taskId, setTaskId] = useState(null);
  const [statusUpdates, setStatusUpdates] = useState([]);
  const [taskResult, setTaskResult] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [pendingApproval, setPendingApproval] = useState(null); // Keep approval logic for potential future use

  // --- WebSocket Handlers ---

  // Unified handler for 'task_update' events
  const handleTaskUpdate = useCallback((update) => {
    // Add every update to the status list for visibility
    setStatusUpdates(prev => [...prev, { ...update, receivedAt: new Date() }]);

    // Check if this update signifies task completion or failure
    if (update.taskId === taskId) {
        if (update.status === 'completed' || update.status === 'failed') {
            setTaskResult(update.result || update.details || { message: `Task ended with status: ${update.status}` });
            setError(update.error || (update.status === 'failed' ? (update.details || 'Task failed with unknown error') : null));
            setIsLoading(false); // Task finished
        } else {
            // Optionally update a general 'current status' state here if needed
        }
    } else {
        console.warn(`Received update for unexpected taskId: ${update.taskId} (current: ${taskId})`);
    }
  }, [taskId]); // Depend on taskId

  const handleConnect = useCallback(() => {
     setIsConnected(true);
  }, []);

  const handleDisconnect = useCallback(() => {
     setIsConnected(false);
     if (isLoading) {
       setError("WebSocket disconnected during task execution. Please check your connection and try submitting again.");
       setIsLoading(false);
     }
  }, [isLoading]);

  // Handler for workflow approval requests (kept for potential future use)
  const handleWorkflowApprovalRequired = useCallback((data) => {
    if (data && data.workflow_run_id && data.data_to_approve) {
        setPendingApproval({
            workflow_run_id: data.workflow_run_id,
            data_to_approve: data.data_to_approve,
        });
        setStatusUpdates(prev => [...prev, { message: `Approval required for workflow ${data.workflow_run_id}`, receivedAt: new Date(), status: 'APPROVAL_PENDING' }]);
    } else {
        console.error("Invalid workflow_approval_required event received:", data);
    }
  }, []);

  // --- Input Handlers ---

  const handleInitialTopicChange = (e) => {
    setInitialTopic(e.target.value);
  };

  // --- Effects ---

  // Effect to manage WebSocket connection and listeners
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
        websocketService.connect();
        websocketService.addListener('connect', handleConnect);
        websocketService.addListener('disconnect', handleDisconnect);
        websocketService.addListener('task_update', handleTaskUpdate);
        websocketService.addListener('workflow_approval_required', handleWorkflowApprovalRequired);
    } else {
        console.warn("OrchestratorPanel: No auth token found, WebSocket not connected.");
    }

    return () => {
      websocketService.removeListener('task_update', handleTaskUpdate);
      websocketService.removeListener('connect', handleConnect);
      websocketService.removeListener('disconnect', handleDisconnect);
      websocketService.removeListener('workflow_approval_required', handleWorkflowApprovalRequired);
      // Consider disconnecting if the panel is unmounted, or manage connection globally
      // websocketService.disconnect();
    };
  }, [handleConnect, handleDisconnect, handleTaskUpdate, handleWorkflowApprovalRequired]);

  // Effect to subscribe/unsubscribe when taskId changes
  useEffect(() => {
    if (taskId && isConnected) {
      websocketService.subscribeToTask(taskId);
      return () => {
        websocketService.unsubscribeFromTask(taskId);
      };
    }
  }, [taskId, isConnected]);

  // --- Actions ---

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null); // Clear previous errors

    if (!initialTopic.trim()) {
      setError('Please enter an initial topic for the workflow.');
      return;
    }
    if (!isConnected) {
       setError('WebSocket is not connected. Cannot submit task.');
       return;
    }

    setIsLoading(true);
    setTaskId(null);
    setStatusUpdates([]);
    setTaskResult(null);

    const goal = "income_generation_workflow"; // Hardcoded goal
    const paramsObj = { initial_topic: initialTopic }; // Specific parameter

    try {
      // Use the existing apiService function, assuming it takes goal and parameters
      const response = await apiService.submitOrchestratorTask(goal, paramsObj);

      if (response && response.taskId) {
        setTaskId(response.taskId);
        setStatusUpdates([{ message: `Task ${response.taskId} submitted for goal "${goal}". Status: ${response.status || 'pending'}. Waiting for updates...`, receivedAt: new Date() }]);
        // setIsLoading remains true until completion/failure update
      } else {
        throw new Error(response?.message || "Invalid response from task submission, missing taskId.");
      }
    } catch (err) {
      console.error("Error submitting task:", err);
      const errorMsg = err.data?.error || err.message || 'Failed to submit task.';
      setError(errorMsg);
      setIsLoading(false);
    }
  };

  // --- Approval Handlers (kept for potential future use) ---
  const handleApprovalDecision = async (decision) => {
      if (!pendingApproval) return;
      const { workflow_run_id } = pendingApproval;
      try {
          await apiService.resumeWorkflow(workflow_run_id, decision);
          setStatusUpdates(prev => [...prev, { message: `Workflow ${workflow_run_id} ${decision}.`, receivedAt: new Date(), status: 'ACTION_TAKEN' }]);
          setPendingApproval(null);
      } catch (err) {
          console.error(`Error sending ${decision} decision for workflow ${workflow_run_id}:`, err);
          const errorMsg = err.data?.error || err.message || `Failed to send ${decision} decision.`;
          setError(`Approval Error: ${errorMsg}`);
           setStatusUpdates(prev => [...prev, { message: `Failed to send ${decision} decision for workflow ${workflow_run_id}. Error: ${errorMsg}`, receivedAt: new Date(), status: 'ERROR' }]);
      }
  };

  const handleApprove = () => handleApprovalDecision('approved');
  const handleReject = () => handleApprovalDecision('rejected');


  return (
    <div className="p-6 bg-slate-800 rounded-lg shadow-md border border-slate-700 text-gray-200">
      <h2 className="text-2xl font-semibold mb-4 text-white">Income Generation Workflow</h2>

       <div className="mb-4 text-sm">
         WebSocket Status:
         <span className={`ml-2 font-bold ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
           {isConnected ? 'Connected' : 'Disconnected'}
         </span>
       </div>

      <form onSubmit={handleSubmit}>
        {/* Removed Goal Input */}

        <div className="mb-4">
          <label htmlFor="initialTopic" className="block text-sm font-medium text-gray-300 mb-1">
            Initial Topic:
          </label>
          <input
            type="text"
            id="initialTopic"
            value={initialTopic}
            onChange={handleInitialTopicChange}
            placeholder="e.g., Develop an AI tool for indie game developers"
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            required
            disabled={isLoading}
          />
           {/* Removed JSON validation messages */}
        </div>

        <button
          type="submit"
          className={`bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md transition duration-200 ease-in-out ${isLoading || !isConnected ? 'opacity-50 cursor-not-allowed' : ''}`}
          disabled={isLoading || !isConnected}
        >
          {isLoading ? 'Processing...' : 'Start Workflow'}
        </button>
      </form>

      {/* Display general errors */}
      {error && (
        <div className="mt-4 p-3 bg-red-900/50 border border-red-700 text-red-300 rounded-md">
          Error: {typeof error === 'string' ? error : JSON.stringify(error)}
        </div>
      )}

      {taskId && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-2 text-white">Workflow Progress (Task ID: {taskId})</h3>
          <div className="p-4 bg-slate-900 rounded-md border border-slate-700 max-h-96 overflow-y-auto"> {/* Increased max-height */}
            {statusUpdates.length === 0 && !taskResult && <p className="text-gray-400 italic">Waiting for updates...</p>}
            <ul className="space-y-2 text-sm">
              {statusUpdates.map((update, index) => (
                <li key={index} className="text-gray-300">
                  <span className="text-gray-500 mr-2">[{update.receivedAt?.toLocaleTimeString() || 'N/A'}]</span>
                  {/* Display relevant info from the update object */}
                  <span className="font-medium">{update.status ? `[${update.status.toUpperCase()}] ` : ''}</span>
                  {update.message || update.details || JSON.stringify(update, (key, value) => key === 'receivedAt' ? undefined : value)}
                </li>
              ))}
            </ul>
            {taskResult && !isLoading && ( // Show result only when not loading anymore
              <div className="mt-4 pt-4 border-t border-slate-700">
                 <h4 className={`font-semibold mb-1 ${error ? 'text-red-400' : 'text-green-400'}`}>
                   {error ? 'Workflow Failed' : 'Workflow Completed!'}
                 </h4>
                <pre className="text-xs bg-slate-800 p-2 rounded overflow-x-auto whitespace-pre-wrap break-words">
                  {typeof taskResult === 'string' ? taskResult : JSON.stringify(taskResult, null, 2)}
                </pre>
                {error && typeof error !== 'object' && ( // Display simple error string if not object
                    <pre className="text-xs text-red-300 bg-red-900/30 p-2 rounded mt-2 whitespace-pre-wrap break-words">
                        Error Details: {error}
                    </pre>
                )}
              </div>
            )}
             {isLoading && !taskResult && (
                 <div className="mt-4 pt-4 border-t border-slate-700 text-center text-indigo-400 animate-pulse">
                     Workflow is running...
                 </div>
             )}
          </div>
        </div>
      )}

      {/* Workflow Approval Section (kept for potential future use) */}
      {pendingApproval && (
        <div className="mt-6 p-4 bg-yellow-900/30 border border-yellow-700 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-3 text-yellow-200">Workflow Approval Required</h3>
          <p className="text-sm text-yellow-300 mb-1">Workflow Run ID: <span className="font-mono">{pendingApproval.workflow_run_id}</span></p>
          <p className="text-sm text-yellow-300 mb-2">Data to Approve/Reject:</p>
          <pre className="text-xs bg-slate-800 p-3 rounded overflow-x-auto whitespace-pre-wrap break-words border border-slate-600 text-gray-200 mb-4">
            {JSON.stringify(pendingApproval.data_to_approve, null, 2)}
          </pre>
          <div className="flex space-x-3">
            <button
              onClick={handleApprove}
              className="bg-green-600 hover:bg-green-500 text-white font-semibold py-2 px-4 rounded-md transition duration-200 ease-in-out"
            >
              Approve
            </button>
            <button
              onClick={handleReject}
              className="bg-red-600 hover:bg-red-500 text-white font-semibold py-2 px-4 rounded-md transition duration-200 ease-in-out"
            >
              Reject
            </button>
          </div>
        </div>
      )}

    </div>
  );
};

export default OrchestratorPanel;