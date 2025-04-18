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

  // --- WebSocket Handlers ---

  // Unified handler for 'task_update' events
  const handleTaskUpdate = useCallback((update) => {
    console.log("Received task update:", update);

    // Add every update to the status list for visibility
    setStatusUpdates(prev => [...prev, { ...update, receivedAt: new Date() }]);

    // Check if this update signifies task completion or failure
    if (update.taskId === taskId) {
        if (update.status === 'completed' || update.status === 'failed') {
            setTaskResult(update.result || update.details || { message: `Task ended with status: ${update.status}` });
            setError(update.error || (update.status === 'failed' ? (update.details || 'Task failed with unknown error') : null));
            setIsLoading(false); // Task finished
            console.log(`Task ${taskId} finished with status: ${update.status}`);
        } else {
            // Optionally update a general 'current status' state here if needed
            console.log(`Task ${taskId} status updated: ${update.status}`);
        }
    } else {
        console.warn(`Received update for unexpected taskId: ${update.taskId} (current: ${taskId})`);
    }
  }, [taskId]); // Depend on taskId to ensure we're processing updates for the current task

  const handleConnect = useCallback(() => {
     console.log("WebSocket connected in component.");
     setIsConnected(true);
  }, []);

  const handleDisconnect = useCallback(() => {
     console.log("WebSocket disconnected in component.");
     setIsConnected(false);
     // Optionally reset task state if connection is lost during processing
     // if (isLoading) {
     //   setError("WebSocket disconnected during task processing.");
     //   setIsLoading(false);
     // }
  }, []);

  // Handler for workflow approval requests
  const handleWorkflowApprovalRequired = useCallback((data) => {
    console.log("Received workflow approval request:", data);
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

  // --- Effects ---

  // Effect to manage WebSocket connection and listeners
  useEffect(() => {
    // Assuming connect needs to happen after login/auth token is available
    // For now, connect on mount. In a real app, trigger this after login.
    const token = localStorage.getItem('authToken'); // Or get from auth context
    if (token) { // Only connect if authenticated
        websocketService.connect(token);
        websocketService.addListener('connect', handleConnect);
        websocketService.addListener('disconnect', handleDisconnect);
        // Listen for the unified task update event
        websocketService.addListener('task_update', handleTaskUpdate);
        // Add listeners for connect/disconnect for status display
        websocketService.addListener('connect', handleConnect);
        websocketService.addListener('disconnect', handleDisconnect);
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
      console.log("OrchestratorPanel unmounted, listeners removed.");
    };
  }, [handleConnect, handleDisconnect, handleTaskUpdate, handleWorkflowApprovalRequired]); // Update dependencies

  // Effect to subscribe/unsubscribe when taskId changes
  useEffect(() => {
    if (taskId && isConnected) {
      console.log(`Subscribing to task ${taskId}`);
      websocketService.subscribeToTask(taskId);

      // Cleanup function to unsubscribe when taskId changes or component unmounts
      return () => {
        console.log(`Unsubscribing from task ${taskId}`);
        websocketService.unsubscribeFromTask(taskId);
      };
    }
  }, [taskId, isConnected]); // Depend on taskId and connection status

  // --- Actions ---

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!goal.trim()) {
      setError('Please enter a goal for the orchestrator.');
      return;
    }
    if (!isConnected) {
       setError('WebSocket is not connected. Cannot submit task.');
       return;
    }


    setIsLoading(true);
    setError(null);
    setTaskId(null);
    setStatusUpdates([]);
    setTaskResult(null);

    try {
      // Basic JSON parsing for parameters for now
      let paramsObj = {};
      if (parameters.trim()) {
        try {
          paramsObj = JSON.parse(parameters);
        } catch (parseError) {
          setError('Invalid JSON format for parameters.');
          setIsLoading(false);
          return;
        }
      }

      const response = await apiService.submitOrchestratorTask(goal, paramsObj);
      console.log("Task submission response:", response);
      if (response && response.taskId) {
        setTaskId(response.taskId);
        // Add initial submission status to updates
        setStatusUpdates([{ message: `Task ${response.taskId} submitted. Status: ${response.status || 'pending'}. Waiting for updates...`, receivedAt: new Date() }]);
        // setIsLoading will remain true until a final result/error is received via WebSocket
      } else {
        throw new Error(response.message || "Invalid response from task submission, missing taskId.");
      }
    } catch (err) {
      console.error("Error submitting task:", err);
      const errorMsg = err.data?.error || err.message || 'Failed to submit task.';
      setError(errorMsg);
      setIsLoading(false);
    }
  };

  // --- Approval Handlers ---
  const handleApprovalDecision = async (decision) => {
      if (!pendingApproval) return;

      const { workflow_run_id } = pendingApproval;
      console.log(`Submitting decision '${decision}' for workflow ${workflow_run_id}`);
      // Optionally add loading state specific to approval
      try {
          await apiService.resumeWorkflow(workflow_run_id, decision);
          console.log(`Workflow ${workflow_run_id} ${decision} signal sent successfully.`);
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
            onChange={(e) => setParameters(e.target.value)}
            placeholder='e.g., {"name": "My AI Blog", "topic": "Artificial Intelligence"}'
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-sm"
            disabled={isLoading}
          />
           <p className="text-xs text-gray-400 mt-1">Enter parameters as a valid JSON object or leave blank.</p>
        </div>

        <button
          type="submit"
          className={`bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md transition duration-200 ease-in-out ${isLoading || !isConnected ? 'opacity-50 cursor-not-allowed' : ''}`}
          disabled={isLoading || !isConnected}
        >
          {isLoading ? 'Processing...' : 'Submit Task'}
        </button>
      </form>

      {error && (
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