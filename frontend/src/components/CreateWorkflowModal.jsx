import React, { useState } from 'react';
import apiService from '../services/api'; // Import the API service

function CreateWorkflowModal({ isOpen, onClose, onWorkflowCreated }) { // Add onWorkflowCreated prop
  const [workflowName, setWorkflowName] = useState('');
  const [description, setDescription] = useState('');
  const [triggerType, setTriggerType] = useState('Manual'); // Default value
  const [actionType, setActionType] = useState('Send Email'); // Default value

  if (!isOpen) return null;

  const handleSubmit = async (event) => {
    event.preventDefault();
    const formData = {
      name: workflowName,
      description: description,
      triggerType: triggerType,
      actionType: actionType,
    };

    console.log('Submitting workflow data:', formData);

    try {
      // Use apiService to create workflow
      const result = await apiService.createWorkflow(formData);

      console.log('API Success:', result);
      alert('Workflow created successfully!'); // Simple success feedback

      // Call the callback function if it exists
      if (onWorkflowCreated) {
        onWorkflowCreated();
      }

      onClose(); // Close modal on success
    } catch (error) {
      console.error('Network or other error:', error);
      alert(`Failed to submit workflow: ${error.message}`);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex justify-center items-center z-50 backdrop-blur-sm"> {/* Darker overlay with blur */}
      <div className="bg-slate-800 p-8 rounded-xl shadow-2xl w-full max-w-lg border border-slate-700"> {/* Dark bg, more padding, larger rounding/shadow, wider, border */}
        <div className="flex justify-between items-center mb-6 pb-3 border-b border-slate-700"> {/* More margin, added border bottom */}
          <h2 className="text-2xl font-bold text-gray-100">Create New Workflow</h2> {/* Larger, bolder, lighter text */}
          <button onClick={onClose} className="text-gray-400 hover:text-gray-100 text-3xl leading-none focus:outline-none">&times;</button> {/* Lighter text, larger, better alignment */}
        </div>
        <form onSubmit={handleSubmit}>
          {/* Workflow Name */}
          <div className="mb-4">
            <label htmlFor="workflowName" className="block text-sm font-medium text-gray-300 mb-2">
              Workflow Name
            </label>
            <input
              type="text"
              id="workflowName"
              name="workflowName"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              required // Make name required
              className="w-full px-4 py-2.5 bg-slate-700 border border-slate-600 text-gray-100 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder-gray-500"
              placeholder="e.g., Send Welcome Email"
            />
          </div>

          {/* Workflow Description */}
          <div className="mb-4">
            <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-2">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              rows="3"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-700 border border-slate-600 text-gray-100 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder-gray-500"
              placeholder="Describe what this workflow does"
            ></textarea>
          </div>

          {/* Trigger Type */}
          <div className="mb-4">
            <label htmlFor="triggerType" className="block text-sm font-medium text-gray-300 mb-2">
              Trigger Type
            </label>
            <select
              id="triggerType"
              name="triggerType"
              value={triggerType}
              onChange={(e) => setTriggerType(e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-700 border border-slate-600 text-gray-100 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="Manual">Manual</option>
              <option value="Scheduled">Scheduled</option>
              <option value="Webhook">Webhook</option>
            </select>
          </div>

          {/* Action Type */}
          <div className="mb-6">
            <label htmlFor="actionType" className="block text-sm font-medium text-gray-300 mb-2">
              Action Type
            </label>
            <select
              id="actionType"
              name="actionType"
              value={actionType}
              onChange={(e) => setActionType(e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-700 border border-slate-600 text-gray-100 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="Send Email">Send Email</option>
              <option value="Log Data">Log Data</option>
              {/* Add more actions as needed */}
            </select>
          </div>

          {/* Buttons */}
          <div className="flex justify-end space-x-4 mt-8 pt-4 border-t border-slate-700">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2 bg-slate-600 text-gray-200 rounded-lg hover:bg-slate-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-800 focus:ring-slate-500 transition duration-150 ease-in-out"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-800 focus:ring-indigo-500 transition duration-150 ease-in-out shadow hover:shadow-md"
            >
              Create Workflow
            </button>
          </div>
        </form>
      </div>
      {/* Optional: Close modal by clicking overlay */}
      {/* <div className="fixed inset-0 z-40" onClick={onClose}></div> */}
    </div>
  );
}

export default CreateWorkflowModal;