import React, { useState, useEffect, useCallback } from 'react';
import apiService from '../services/api';
import websocketService from '../services/websocketService';

const OrchestratorPanel = () => {
  const [goal, setGoal] = useState('');
  const [parameters, setParameters] = useState(''); // Simple string input for now
  const [taskId, setTaskId] = useState(null);
  const [statusUpdates, setStatusUpdates] = useState([]);
  const [taskResult, setTaskResult] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [pendingApproval, setPendingApproval] = useState(null); // State for pending approval
  const [parametersError, setParametersError] = useState(null); // State for parameter JSON error

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
  }, [taskId]); // Depend on taskId to ensure we're processing updates for the current task

  const handleConnect = useCallback(() => {
     setIsConnected(true);
  }, []);

  const handleDisconnect = useCallback(() => {
     setIsConnected(false);
     // Optionally reset task state if connection is lost during processing
     if (isLoading) {
       setError("WebSocket disconnected during task execution. Please check your connection and try submitting again.");
       setIsLoading(false);
     }
  }, [isLoading]); // Added isLoading dependency

  // Handler for workflow approval requests
  const handleWorkflowApprovalRequired = useCallback((data) => {
    if (data && data.workflow_run_id && data.data_to_approve) {
        setPendingApproval({
            workflow_run_id: data.workflow_run_id,
            data_to_approve: data.data_to_approve,
        });
        // Optionally, add a status update to indicate approval is needed
        setStatusUpdates(prev => [...prev, { message: `Approval required for workflow ${data.workflow_run_id}`, receivedAt: new Date(), status: 'APPROVAL_PENDING' }]);
    } else {
        console.error("Invalid workflow_approval_required event received:", data);
    }
  }, []); // No dependencies needed as it only sets state

  // --- Input Handlers ---

  const handleParametersChange = (e) => {
    const newValue = e.target.value;
    setParameters(newValue);

    if (newValue.trim() === '') {
      setParametersError(null); // Clear error if empty
      return;
    }

    try {
      JSON.parse(newValue);
      setParametersError(null); // Clear error if valid JSON
    } catch (parseError) {
      setParametersError('Invalid JSON format.'); // Set error if invalid
    }
  };

  // --- Effects ---

  // Effect to manage WebSocket connection and listeners
  useEffect(() => {
    // Assuming connect needs to happen after login/auth token is available
    // For now, connect on mount. In a real app, trigger this after login.
    const token = localStorage.getItem('authToken'); // Or get from auth context
    if (token) { // Only connect if authenticated
        // Use connect without token argument as per Task 2 changes
        websocketService.connect();
        websocketService.addListener('connect', handleConnect);
        websocketService.addListener('disconnect', handleDisconnect);
        // Listen for the unified task update event
        websocketService.addListener('task_update', handleTaskUpdate);
        // Listen for workflow approval requests
        websocketService.addListener('workflow_approval_required', handleWorkflowApprovalRequired);
    } else {
        console.warn("OrchestratorPanel: No auth token found, WebSocket not connected.");
    }


    // Cleanup on unmount
    return () => {
      // Remove all listeners added in this effect
      websocketService.removeListener('task_update', handleTaskUpdate);
      websocketService.removeListener('connect', handleConnect);
      websocketService.removeListener('disconnect', handleDisconnect);
      websocketService.removeListener('workflow_approval_required', handleWorkflowApprovalRequired); // Remove approval listener
      // Consider disconnecting if the panel is unmounted, or manage connection globally
      // websocketService.disconnect();
    };
  }, [handleConnect, handleDisconnect, handleTaskUpdate, handleWorkflowApprovalRequired]); // Update dependencies

  // Effect to subscribe/unsubscribe when taskId changes
  useEffect(() => {
    if (taskId && isConnected) {
      websocketService.subscribeToTask(taskId);

      // Cleanup function to unsubscribe when taskId changes or component unmounts
      return () => {
        websocketService.unsubscribeFromTask(taskId);
      };
    }
  }, [taskId, isConnected]); // Depend on taskId and connection status

  // --- Actions ---

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null); // Clear previous general errors
    setParametersError(null); // Clear parameter error on new submit attempt (re-validated below)

    if (!goal.trim()) {
      setError('Please enter a goal for the orchestrator.');
      return;
    }
    if (!isConnected) {
       setError('WebSocket is not connected. Cannot submit task.');
       return;
    }

    // Re-validate parameters JSON just before submit
    let paramsObj = {};
    if (parameters.trim()) {
        try {
          paramsObj = JSON.parse(parameters);
          setParametersError(null); // Ensure error is clear if parsing succeeds here
        } catch (parseError) {
          setParametersError('Invalid JSON format.'); // Set error
          // setError('Please fix the invalid JSON format in parameters before submitting.'); // Optional: set general error too
          return; // Prevent submission
        }
    } else {
        setParametersError(null); // Clear error if parameters are empty
    }

    // If validation passed above, proceed
    setIsLoading(true);
    setTaskId(null);
    setStatusUpdates([]);
    setTaskResult(null);

    try {
      // paramsObj is already parsed and validated above
      const response = await apiService.submitOrchestratorTask(goal, paramsObj);

      if (response && response.taskId) {
        setTaskId(response.taskId);
        // Add initial submission status to updates
        setStatusUpdates([{ message: `Task ${response.taskId} submitted. Status: ${response.status || 'pending'}. Waiting for updates...`, receivedAt: new Date() }]);
        // setIsLoading will remain true until a final result/error is received via WebSocket
      } else {
        throw new Error(response?.message || "Invalid response from task submission, missing taskId.");
      }
    } catch (err) {
      console.error("Error submitting task:", err);
      const errorMsg = err.data?.error || err.message || 'Failed to submit task.';
      setError(errorMsg); // Set general error state
      setIsLoading(false);
    }
  };

  // --- Approval Handlers ---
  const handleApprovalDecision = async (decision) => {
      if (!pendingApproval) return;

      const { workflow_run_id } = pendingApproval;
      // Optionally add loading state specific to approval
      try {
          await apiService.resumeWorkflow(workflow_run_id, decision);
          // Add a status update confirming the action
          setStatusUpdates(prev => [...prev, { message: `Workflow ${workflow_run_id} ${decision}.`, receivedAt: new Date(), status: 'ACTION_TAKEN' }]);
          setPendingApproval(null); // Clear the approval request
      } catch (err) {
          console.error(`Error sending ${decision} decision for workflow ${workflow_run_id}:`, err);
          const errorMsg = err.data?.error || err.message || `Failed to send ${decision} decision.`;
          // Display error near the approval section or reuse the main error state
          setError(`Approval Error: ${errorMsg}`); // Or use a dedicated approval error state
          // Optionally add a status update about the error
           setStatusUpdates(prev => [...prev, { message: `Failed to send ${decision} decision for workflow ${workflow_run_id}. Error: ${errorMsg}`, receivedAt: new Date(), status: 'ERROR' }]);
      } finally {
          // Clear approval-specific loading state if used
      }
  };

  const handleApprove = () => handleApprovalDecision('approved');
  const handleReject = () => handleApprovalDecision('rejected');


  return (
    <div className="p-6 bg-slate-800 rounded-lg shadow-md border border-slate-700 text-gray-200">
      <h2 className="text-2xl font-semibold mb-4 text-white">Orchestrator Control Panel</h2>

       <div className="mb-4 text-sm">
         WebSocket Status:
         <span className={`ml-2 font-bold ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
           {isConnected ? 'Connected' : 'Disconnected'}
         </span>
       </div>

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="goal" className="block text-sm font-medium text-gray-300 mb-1">
            Goal / Task Description:
          </label>
          <input
            type="text"
            id="goal"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="e.g., create_membership_site, analyze_market_segment"
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            required
            disabled={isLoading}
          />
        </div>

        <div className="mb-4">
          <label htmlFor="parameters" className="block text-sm font-medium text-gray-300 mb-1">
            Parameters (JSON format):
          </label>
          <textarea
            id="parameters"
            rows="3"
            value={parameters}
            onChange={handleParametersChange} // Use the validation handler
            placeholder='e.g., {"name": "My AI Blog", "topic": "Artificial Intelligence"}'
            className={`w-full px-3 py-2 bg-slate-700 border rounded-md text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-sm ${parametersError ? 'border-red-500' : 'border-slate-600'}`} // Add red border on error
            disabled={isLoading}
          />
           <p className="text-xs text-gray-400 mt-1">Enter parameters as a valid JSON object or leave blank.</p>
           {parametersError && ( // Display JSON validation error
             <p className="text-xs text-red-400 mt-1">{parametersError}</p>
           )}
        </div>

        <button
          type="submit"
          className={`bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md transition duration-200 ease-in-out ${isLoading || !isConnected || parametersError ? 'opacity-50 cursor-not-allowed' : ''}`} // Disable on param error too
          disabled={isLoading || !isConnected || !!parametersError} // Disable button if params are invalid
        >
          {isLoading ? 'Processing...' : 'Submit Task'}
        </button>
      </form>

      {/* Display general errors (not parameter-specific ones shown above) */}
      {error && !parametersError && (
        <div className="mt-4 p-3 bg-red-900/50 border border-red-700 text-red-300 rounded-md">
          Error: {error}
        </div>
      )}

      {taskId && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-2 text-white">Task Progress (ID: {taskId})</h3>
          <div className="p-4 bg-slate-900 rounded-md border border-slate-700 max-h-60 overflow-y-auto">
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
                   {error ? 'Task Failed' : 'Task Completed!'}
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
                     Task is running...
                 </div>
             )}
          </div>
        </div>
      )}

      {/* Workflow Approval Section */}
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
           {/* Display approval-specific errors here if needed */}
        </div>
      )}

    </div>
  );
};

export default OrchestratorPanel;