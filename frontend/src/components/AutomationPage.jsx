import React, { useState } from 'react';
import CreateWorkflowModal from './CreateWorkflowModal'; // Import the modal component

const AutomationPage = () => {
  const [isModalOpen, setIsModalOpen] = useState(false); // State for modal visibility

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  return (
    <div className="p-6 md:p-10 text-gray-100">
      <h1 className="text-3xl font-bold mb-6 text-white">Automation Hub</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Workflow Management Card */}
        <div className="bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-3 text-white">Workflow Management</h2>
          <p className="text-gray-400">
            View, create, and manage your automated workflows. Streamline repetitive tasks and processes.
          </p>
          {/* Placeholder for buttons or links */}
          <div className="mt-4 flex flex-col space-y-4">
            {/* Create New Workflow Button */}
            <button
              onClick={openModal} // Open the modal on click
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded self-start"
            >
              Create New Workflow
            </button>

            {/* Placeholder for Existing Workflows List */}
            <div className="mt-4 p-4 border border-gray-700 rounded bg-gray-900 text-gray-500">
              Existing workflows will be listed here.
            </div>
          </div>
        </div>

        {/* Scheduled Tasks/Reports Card */}
        <div className="bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-3 text-white">Scheduled Tasks & Reports</h2>
          <p className="text-gray-400">
            Set up and monitor scheduled tasks or generate automated reports based on your data.
          </p>
           {/* Placeholder for list or status */}
           <div className="mt-4 text-gray-500">
             (List of scheduled tasks or configuration options will go here)
           </div>
        </div>

        {/* API Integrations Card */}
        <div className="bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-3 text-white">API Integrations</h2>
          <p className="text-gray-400">
            Connect third-party applications and services via API to enhance your automation capabilities.
          </p>
          {/* Placeholder for connection status or list */}
          <div className="mt-4 text-gray-500">
            (List of connected apps or integration settings will go here)
          </div>
        </div>
      </div>

      {/* Render the modal conditionally */}
      <CreateWorkflowModal isOpen={isModalOpen} onClose={closeModal} />
    </div>
  );
};

export default AutomationPage;