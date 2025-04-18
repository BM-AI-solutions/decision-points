import React, { useState, useEffect } from 'react';
import CreateWorkflowModal from './CreateWorkflowModal'; // Import the modal component
import apiService from '../services/api'; // Import the API service

const AutomationPage = () => {
  const [isModalOpen, setIsModalOpen] = useState(false); // State for modal visibility
  const [workflows, setWorkflows] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);


  // Function to fetch workflows
  const fetchWorkflows = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiService.getWorkflows();
      setWorkflows(data || []); // Ensure workflows is always an array
    } catch (err) {
      console.error("Error fetching workflows:", err);
      setError(err.data?.message || 'Failed to fetch workflows.');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch workflows on component mount
  useEffect(() => {
    fetchWorkflows();
  }, []); // Empty dependency array ensures this runs only once on mount

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  return (
    <div className="p-8 md:p-12 text-gray-200 min-h-screen"> {/* Increased padding, lighter base text */}
      <h1 className="text-4xl font-bold mb-10 text-white">Automation Hub</h1> {/* Larger heading, more margin */}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"> {/* Increased gap */}
        {/* Workflow Management Card */}
        <div className="bg-slate-800 p-6 rounded-xl shadow-lg border border-slate-700 transition-transform duration-200 hover:scale-[1.02]"> {/* Changed bg, increased rounding, added border, shadow, hover effect */}
          <h2 className="text-2xl font-semibold mb-4 text-gray-100">Workflow Management</h2> {/* Larger heading, more margin, lighter text */}
          <p className="text-gray-400 leading-relaxed mb-5"> {/* Added line-height and bottom margin */}
            View, create, and manage your automated workflows. Streamline repetitive tasks and processes.
          </p>
          {/* Placeholder for buttons or links */}
          <div className="mt-4 flex flex-col space-y-4">
            {/* Create New Workflow Button */}
            <button
              onClick={openModal} // Open the modal on click
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 px-6 rounded-lg self-start transition duration-200 ease-in-out shadow hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-800" // Enhanced button styles
            >
              Create New Workflow +
            </button> {/* Added '+' for visual cue */}

            {/* Existing Workflows List */}
            <div className="mt-6">
              <h3 className="text-xl font-semibold mb-3 text-gray-200">Your Workflows</h3>
              {isLoading ? (
                <div className="text-center text-gray-400 py-4">Loading workflows...</div>
              ) : error ? (
                <div className="text-center text-red-500 bg-red-900/30 border border-red-700 p-4 rounded-lg">
                  Error: {error}
                </div>
              ) : workflows.length > 0 ? (
                <ul className="space-y-3">
                  {workflows.map((workflow) => (
                    <li key={workflow.id || workflow.name} className="bg-slate-700 p-4 rounded-lg shadow flex justify-between items-center">
                      <span className="text-gray-100">{workflow.name}</span>
                      {/* Add more details or actions here if needed */}
                      <span className="text-xs text-gray-400">ID: {workflow.id}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-center text-gray-400 py-4 border-2 border-dashed border-slate-700 rounded-lg bg-slate-900/50">
                  No workflows created yet.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Scheduled Tasks/Reports Card */}
        <div className="bg-slate-800 p-6 rounded-xl shadow-lg border border-slate-700 transition-transform duration-200 hover:scale-[1.02]"> {/* Consistent card styling */}
          <h2 className="text-2xl font-semibold mb-4 text-gray-100">Scheduled Tasks & Reports</h2> {/* Consistent heading */}
          <p className="text-gray-400 leading-relaxed mb-5"> {/* Consistent text styling */}
            Set up and monitor scheduled tasks or generate automated reports based on your data.
          </p>
           {/* Placeholder for list or status */}
           <div className="mt-4 text-gray-500 italic"> {/* Italicized placeholder */}
             (List of scheduled tasks or configuration options will go here)
           </div>
        </div>

        {/* API Integrations Card */}
        <div className="bg-slate-800 p-6 rounded-xl shadow-lg border border-slate-700 transition-transform duration-200 hover:scale-[1.02]"> {/* Consistent card styling */}
          <h2 className="text-2xl font-semibold mb-4 text-gray-100">API Integrations</h2> {/* Consistent heading */}
          <p className="text-gray-400 leading-relaxed mb-5"> {/* Consistent text styling */}
            Connect third-party applications and services via API to enhance your automation capabilities.
          </p>
          {/* Placeholder for connection status or list */}
          <div className="mt-4 text-gray-500 italic"> {/* Italicized placeholder */}
            (List of connected apps or integration settings will go here)
          </div>
        </div>
      </div>

      {/* Render the modal conditionally */}
      <CreateWorkflowModal isOpen={isModalOpen} onClose={closeModal} onWorkflowCreated={fetchWorkflows} />
    </div>
  );
};

export default AutomationPage;