import React, { useState } from 'react';
import AgentTaskMonitor from '../components/AgentTaskMonitor';

/**
 * A test page for the multi-agent workflow.
 */
const AgentTestPage = () => {
  const [prompt, setPrompt] = useState('');
  const [activeTask, setActiveTask] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (prompt.trim()) {
      setActiveTask(prompt);
    }
  };

  const handleComplete = (result) => {
    console.log('Task completed with result:', result);
  };

  const handleError = (error) => {
    console.error('Task failed with error:', error);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Multi-Agent Workflow Test</h1>
      
      <div className="mb-8">
        <form onSubmit={handleSubmit} className="flex flex-col md:flex-row gap-4">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter a prompt for the agents..."
            className="form-input flex-grow"
          />
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={!prompt.trim()}
          >
            Submit
          </button>
        </form>
      </div>
      
      {activeTask && (
        <div className="mb-8">
          <AgentTaskMonitor
            initialPrompt={activeTask}
            onComplete={handleComplete}
            onError={handleError}
          />
        </div>
      )}
      
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">How to Use</h2>
        <ol className="list-decimal pl-6 space-y-2">
          <li>Enter a prompt in the input field above.</li>
          <li>Click "Submit" to start the multi-agent workflow.</li>
          <li>Watch the agents work together to complete the task.</li>
          <li>View the real-time updates and final result.</li>
        </ol>
        
        <h3 className="text-lg font-bold mt-6 mb-2">Example Prompts:</h3>
        <ul className="list-disc pl-6 space-y-2">
          <li>
            <button 
              className="text-blue-400 hover:underline"
              onClick={() => setPrompt("Research the market for AI-powered content generation tools.")}
            >
              Research the market for AI-powered content generation tools.
            </button>
          </li>
          <li>
            <button 
              className="text-blue-400 hover:underline"
              onClick={() => setPrompt("Generate a blog post about the future of remote work.")}
            >
              Generate a blog post about the future of remote work.
            </button>
          </li>
          <li>
            <button 
              className="text-blue-400 hover:underline"
              onClick={() => setPrompt("Find potential leads for a SaaS product in the healthcare industry.")}
            >
              Find potential leads for a SaaS product in the healthcare industry.
            </button>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default AgentTestPage;
