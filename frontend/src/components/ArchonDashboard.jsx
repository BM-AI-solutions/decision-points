import React, { useState, useEffect } from 'react';
// Import the refactored apiService
import apiService from '../services/api.js';

function ArchonDashboard() {
  const [incomeStreams, setIncomeStreams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedStream, setSelectedStream] = useState(null); // To hold the currently selected stream details
  const [activeTab, setActiveTab] = useState('overview'); // State for active tab
  const [showForm, setShowForm] = useState(false); // State for form visibility
  const [isSubmitting, setIsSubmitting] = useState(false); // State for form submission loading
  const [formError, setFormError] = useState(null); // State for form errors
  const initialFormData = {
      name: '',
      stream_type: '',
      description: '',
      automation_level: 8,
      required_services: []
  };
  const [formData, setFormData] = useState(initialFormData); // State for form data
  const [agentParams, setAgentParams] = useState('{}'); // State for agent parameters textarea
  const [agentResult, setAgentResult] = useState(null); // State for agent run result
  const [isAgentRunning, setIsAgentRunning] = useState(false); // State for agent loading
  const [forecastParams, setForecastParams] = useState({ months: 12, growth_rate: 5.0 }); // State for forecast inputs
  const [forecastResult, setForecastResult] = useState(null); // State for forecast result
  const [isForecasting, setIsForecasting] = useState(false); // State for forecast loading
  // State variables already added in the previous (failed) attempt, no change needed here.


  useEffect(() => {
    const fetchStreams = async () => { // Define fetchStreams inside useEffect
      try {
        setLoading(true);
        setError(null);
          // Use the imported api instance
          // The ApiClient returns the data directly on success
          // The backend route seems to return { success: true, data: [...] }
          const result = await api.get('/archon/income-streams');
          if (result && result.success) {
              setIncomeStreams(result.data);
              if (result.data.length > 0) {
                setSelectedStream(result.data[0]); // Select the first stream by default
              }
          } else {
              // Handle cases where the API call succeeded but the operation failed
               throw new Error(result.error || 'Failed to fetch streams from API');
          }
        } catch (err) {
          console.error("Error fetching income streams:", err);
          // Use error details from ApiClient if available
          const message = err?.data?.message || err?.message || 'Failed to load income streams.';
          setError(message);
        } finally {
          setLoading(false);
        }
      };

      fetchStreams(); // Call fetchStreams inside useEffect
  }, []); // Empty dependency array ensures this runs only once on mount

  const handleSelectStream = (stream) => {
    setSelectedStream(stream);
    setActiveTab('overview'); // Reset to overview tab when selecting a new stream
    setShowForm(false); // Hide form when selecting a stream
  };

  const handleInputChange = (e) => {
      const { name, value, type, checked } = e.target;
      if (type === 'checkbox') {
          setFormData(prev => ({
              ...prev,
              required_services: checked
                  ? [...prev.required_services, value]
                  : prev.required_services.filter(service => service !== value)
          }));
      } else if (type === 'range') {
           setFormData(prev => ({ ...prev, [name]: parseInt(value, 10) }));
      }
      else {
          setFormData(prev => ({ ...prev, [name]: value }));
      }
  };

  const handleCreateStreamSubmit = async (e) => {
      e.preventDefault();
      setIsSubmitting(true);
      setFormError(null);
      try {
          const newStream = await api.post('/archon/income-streams', formData);
          if (newStream && newStream.success) {
              setShowForm(false);
              setFormData(initialFormData); // Reset form
              await fetchStreams(); // Refresh the list
              // Optionally select the newly created stream
              // Find the stream in the updated list or use the returned data
              // setSelectedStream(newStream.data);
          } else {
              throw new Error(newStream.error || 'Failed to create stream');
          }
      } catch (err) {
          console.error("Error creating income stream:", err);
          const message = err?.data?.message || err?.message || 'Failed to create income stream.';
          setFormError(message);
      } finally {
          setIsSubmitting(false);
      }
  };

  const handleRunAgent = async () => {
      if (!selectedStream) return;
      setIsAgentRunning(true);
      setAgentResult(null); // Clear previous results
      try {
          // Validate JSON if needed before sending
          let parsedParams = {};
          try {
              parsedParams = JSON.parse(agentParams);
          } catch (jsonError) {
              throw new Error("Invalid JSON in Agent Parameters.");
          }

          const result = await api.post('/archon/run-agent', {
              income_stream_id: selectedStream.id,
              agent_parameters: parsedParams // Send parsed JSON object
          });

          if (result && result.success) {
              setAgentResult(result.data); // Store the successful result data
          } else {
              throw new Error(result.error || 'Failed to run agent');
          }
      } catch (err) {
          console.error("Error running Archon agent:", err);
          const message = err?.data?.message || err?.message || 'Failed to run Archon agent.';
          // Display error within the agent result area
          setAgentResult({ error: message });
      } finally {
          setIsAgentRunning(false);
      }
  };

  const handleForecastParamChange = (e) => {
      const { name, value } = e.target;
      setForecastParams(prev => ({
          ...prev,
          [name]: name === 'months' ? parseInt(value, 10) : parseFloat(value)
      }));
  };

  const handleGenerateForecast = async () => {
      if (!selectedStream) return; // Although forecast API doesn't seem to use streamId based on archon.js
      setIsForecasting(true);
      setForecastResult(null); // Clear previous results
      try {
          const result = await api.post('/archon/forecast', forecastParams);
          if (result && result.success) {
              setForecastResult(result.data); // Store the successful result data
          } else {
              throw new Error(result.error || 'Failed to generate forecast');
          }
      } catch (err) {
          console.error("Error generating forecast:", err);
          const message = err?.data?.message || err?.message || 'Failed to generate forecast.';
          // Display error within the forecast result area
          setForecastResult({ error: message });
      } finally {
          setIsForecasting(false);
      }
  };

  // Handler function already added in the previous (failed) attempt, no change needed here.


  const renderTabContent = () => {
    if (!selectedStream) return null;

    switch (activeTab) {
      case 'overview':
        return (
          <div className="income-stream-overview grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="overview-card bg-white border border-gray-300 rounded-md p-5">
              <h4 className="text-lg font-semibold text-gray-700 mb-4">Details</h4>
              <div className="overview-item flex justify-between mb-2 text-sm">
                <span className="label text-gray-600">Type</span>
                <span className="value font-medium">{selectedStream.type}</span>
              </div>
              <div className="overview-item flex justify-between mb-2 text-sm">
                <span className="label text-gray-600">Automation Level</span>
                <span className="value font-medium">{selectedStream.automation_level}/10</span>
              </div>
              <div className="overview-item flex justify-between mb-2 text-sm">
                <span className="label text-gray-600">Automated Percentage</span>
                <span className="value font-medium">{selectedStream.automated_percentage}%</span>
              </div>
              <div className="overview-item flex justify-between text-sm">
                <span className="label text-gray-600">Status</span>
                <span className="value font-medium capitalize">{selectedStream.status}</span>
              </div>
            </div>
            <div className="overview-card bg-white border border-gray-300 rounded-md p-5">
              <h4 className="text-lg font-semibold text-gray-700 mb-4">Revenue Potential</h4>
              <div className="overview-item flex justify-between mb-2 text-sm">
                <span className="label text-gray-600">Monthly Revenue</span>
                <span className="value font-medium">${selectedStream.monthly_revenue?.toFixed(2) ?? 'N/A'}</span>
              </div>
              <div className="overview-item flex justify-between mb-2 text-sm">
                <span className="label text-gray-600">Annual Revenue</span>
                <span className="value font-medium">${(selectedStream.monthly_revenue * 12)?.toFixed(2) ?? 'N/A'}</span>
              </div>
              <div className="overview-item flex justify-between text-sm">
                <span className="label text-gray-600">Required Services</span>
                <span className="value font-medium">{selectedStream.required_services?.join(', ') || 'None'}</span>
              </div>
            </div>
          </div>
        );
      case 'implement':
        return (
          <div className="implement-tab-content">
            <div className="implement-actions bg-white border border-gray-300 rounded-md p-5 mb-6">
              <p className="text-sm text-gray-700 mb-4">Use the Archon Agent to implement this income stream with minimal human intervention.</p>
              <div className="input-group mb-4">
                <label htmlFor="agent-params" className="block mb-1.5 font-medium text-sm text-gray-700">Agent Parameters (JSON)</label>
                <textarea
                    id="agent-params"
                    className="form-input w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-300 font-mono h-24"
                    placeholder='Enter agent parameters as JSON, e.g., {"strategy": "aggressive"}'
                    value={agentParams}
                    onChange={(e) => setAgentParams(e.target.value)}
                ></textarea>
              </div>
              <button
                id="run-agent-btn"
                className="btn btn-primary bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition text-sm"
                onClick={handleRunAgent}
                disabled={isAgentRunning || !selectedStream}
              >
                {isAgentRunning ? 'Running Agent...' : 'Run Archon Agent'}
              </button>
            </div>

            {/* Agent Result Area */}
            {(isAgentRunning || agentResult) && (
                 <div id="agent-result" className="agent-result bg-white border border-gray-300 rounded-md p-5">
                    {isAgentRunning && <p>Running Archon Agent, please wait...</p>}
                    {agentResult && agentResult.error && (
                        <p className="text-red-600">Failed to run Archon agent: {agentResult.error}</p>
                    )}
                    {agentResult && !agentResult.error && (
                         <>
                            <div className="result-section mb-6">
                                <h4 className="text-lg font-semibold text-gray-700 mb-3">Archon Agent Configuration</h4>
                                <p className="text-sm text-gray-600 mb-3">The Archon agent has been configured to implement the income stream with the following parameters:</p>
                                <pre className="code-block bg-gray-100 p-3 rounded-md text-xs overflow-x-auto">
                                    {JSON.stringify(agentResult.archon_run_agent_json || agentResult, null, 2)}
                                </pre>
                            </div>
                             <div className="result-section">
                                <h4 className="text-lg font-semibold text-gray-700 mb-3">Next Steps</h4>
                                <ul className="step-list list-decimal list-inside text-sm text-gray-600 space-y-1 pl-1">
                                    <li>Archon agent is analyzing and implementing the income stream.</li>
                                    <li>Once implementation is complete, you can generate a detailed deployment guide.</li>
                                    <li>You can then forecast the revenue and monitor the performance of your income stream.</li>
                                </ul>
                            </div>
                        </>
                    )}
                 </div>
            )}
          </div>
        );
      case 'forecast':
        return (
          <div className="forecast-tab-content">
            <div className="forecast-controls bg-white border border-gray-300 rounded-md p-5 mb-6 flex items-center gap-4 flex-wrap">
              <div className="input-group inline-block">
                <label htmlFor="forecast-months" className="block mb-1 font-medium text-sm text-gray-700">Months</label>
                <input
                    type="number"
                    id="forecast-months"
                    name="months"
                    className="form-input w-24 px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-300"
                    min="1" max="60"
                    value={forecastParams.months}
                    onChange={handleForecastParamChange}
                 />
              </div>
              <div className="input-group inline-block">
                <label htmlFor="growth-rate" className="block mb-1 font-medium text-sm text-gray-700">Monthly Growth (%)</label>
                <input
                    type="number"
                    id="growth-rate"
                    name="growth_rate"
                    className="form-input w-24 px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-300"
                    min="0" max="100" step="0.1"
                    value={forecastParams.growth_rate}
                    onChange={handleForecastParamChange}
                />
              </div>
              <button
                id="generate-forecast-btn"
                className="btn btn-primary bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition text-sm self-end"
                onClick={handleGenerateForecast}
                disabled={isForecasting}
              >
                {isForecasting ? 'Generating...' : 'Generate Forecast'}
              </button>
            </div>

            {/* Forecast Result Area */}
            {(isForecasting || forecastResult) && (
                <div id="forecast-result" className="forecast-result bg-white border border-gray-300 rounded-md p-5">
                    {isForecasting && <p>Generating forecast, please wait...</p>}
                    {forecastResult && forecastResult.error && (
                        <p className="text-red-600">Failed to generate forecast: {forecastResult.error}</p>
                    )}
                    {forecastResult && !forecastResult.error && (
                        <>
                            <div className="forecast-summary grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                                <div className="forecast-metric bg-gray-100 rounded-md p-4 text-center">
                                    <div className="value text-xl font-semibold text-blue-600 mb-1">${forecastResult.average_monthly_revenue?.toFixed(2) ?? 'N/A'}</div>
                                    <div className="label text-xs text-gray-600">Avg Monthly Revenue</div>
                                </div>
                                <div className="forecast-metric bg-gray-100 rounded-md p-4 text-center">
                                    <div className="value text-xl font-semibold text-blue-600 mb-1">${forecastResult.total_projected_revenue?.toFixed(2) ?? 'N/A'}</div>
                                    <div className="label text-xs text-gray-600">Total {forecastParams.months} Month Revenue</div>
                                </div>
                                <div className="forecast-metric bg-gray-100 rounded-md p-4 text-center">
                                    <div className="value text-xl font-semibold text-blue-600 mb-1">{forecastResult.growth_rate_monthly}%</div>
                                    <div className="label text-xs text-gray-600">Monthly Growth Rate</div>
                                </div>
                            </div>

                            <div className="forecast-table">
                                <h4 className="text-lg font-semibold text-gray-700 mb-3">Monthly Projections</h4>
                                <div className="overflow-x-auto">
                                    <table className="table w-full text-sm text-left text-gray-500">
                                        <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                                            <tr>
                                                <th scope="col" className="px-4 py-2">Month</th>
                                                <th scope="col" className="px-4 py-2">Revenue</th>
                                                <th scope="col" className="px-4 py-2">Growth</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {forecastResult.monthly_projections?.map(month => (
                                                <tr key={month.month} className="bg-white border-b hover:bg-gray-50">
                                                    <td className="px-4 py-2">Month {month.month}</td>
                                                    <td className="px-4 py-2">${month.revenue?.toFixed(2) ?? 'N/A'}</td>
                                                    <td className="px-4 py-2">{month.growth ?? 'N/A'}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            {/* TODO: Add Chart visualization if needed */}
                            {/* <div className="forecast-chart w-full h-64 mt-6 bg-gray-200 rounded">Chart Placeholder</div> */}
                        </>
                    )}
                </div>
            )}
          </div>
        );
      case 'deploy':
        return (
          <div className="deploy-tab-content">
            <div className="deployment-actions bg-white border border-gray-300 rounded-md p-5 mb-6">
              <p className="text-sm text-gray-700 mb-4">Generate a comprehensive deployment guide for this income stream.</p>
              <button
                id="generate-guide-btn"
                className="btn btn-primary bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition text-sm"
                onClick={handleGenerateDeploymentGuide}
                disabled={isGeneratingGuide || !selectedStream}
              >
                {isGeneratingGuide ? 'Generating...' : 'Generate Deployment Guide'}
              </button>
            </div>

            {/* Deployment Guide Result Area */}
            {(isGeneratingGuide || deploymentGuideResult) && (
                <div id="deployment-guide" className="deployment-guide bg-white border border-gray-300 rounded-md p-5">
                    {isGeneratingGuide && <p>Generating deployment guide, please wait...</p>}
                    {deploymentGuideResult && deploymentGuideResult.error && (
                        <p className="text-red-600">Failed to generate deployment guide: {deploymentGuideResult.error}</p>
                    )}
                    {deploymentGuideResult && !deploymentGuideResult.error && (
                        <>
                            {/* Deployment Steps */}
                            {deploymentGuideResult.deployment?.steps && (
                                <div className="guide-section mb-6">
                                    <h4 className="text-lg font-semibold text-gray-700 mb-3">Deployment Steps</h4>
                                    <ol className="step-list list-decimal list-inside text-sm text-gray-600 space-y-1 pl-1">
                                        {deploymentGuideResult.deployment.steps.map((step, index) => <li key={index}>{step}</li>)}
                                    </ol>
                                </div>
                            )}

                            {/* Technical Requirements */}
                            {deploymentGuideResult.deployment?.technical_requirements && (
                                <div className="guide-section mb-6">
                                    <h4 className="text-lg font-semibold text-gray-700 mb-3">Technical Requirements</h4>
                                    <ul className="list-disc list-inside text-sm text-gray-600 space-y-1 pl-1">
                                        {deploymentGuideResult.deployment.technical_requirements.map((req, index) => <li key={index}>{req}</li>)}
                                    </ul>
                                    {deploymentGuideResult.deployment.estimated_setup_time && (
                                        <p className="text-sm text-gray-600 mt-2">Estimated setup time: {deploymentGuideResult.deployment.estimated_setup_time}</p>
                                    )}
                                </div>
                            )}

                            {/* Maintenance */}
                            {deploymentGuideResult.maintenance?.recurring_tasks && (
                                <div className="guide-section mb-6">
                                    <h4 className="text-lg font-semibold text-gray-700 mb-3">Maintenance</h4>
                                    <ul className="list-disc list-inside text-sm text-gray-600 space-y-1 pl-1">
                                        {deploymentGuideResult.maintenance.recurring_tasks.map((task, index) => <li key={index}>{task}</li>)}
                                    </ul>
                                     {deploymentGuideResult.maintenance.estimated_weekly_effort && (
                                        <p className="text-sm text-gray-600 mt-2">Estimated weekly effort: {deploymentGuideResult.maintenance.estimated_weekly_effort}</p>
                                    )}
                                </div>
                            )}

                            {/* Profitability */}
                            {deploymentGuideResult.profitability && (
                                <div className="guide-section">
                                    <h4 className="text-lg font-semibold text-gray-700 mb-3">Profitability</h4>
                                    {deploymentGuideResult.profitability.estimated_monthly_revenue && <p className="text-sm text-gray-600">Estimated monthly revenue: ${deploymentGuideResult.profitability.estimated_monthly_revenue.toFixed(2)}</p>}
                                    {deploymentGuideResult.profitability.estimated_annual_revenue && <p className="text-sm text-gray-600">Estimated annual revenue: ${deploymentGuideResult.profitability.estimated_annual_revenue.toFixed(2)}</p>}
                                    {deploymentGuideResult.profitability.estimated_profit_margin && <p className="text-sm text-gray-600">Estimated profit margin: {deploymentGuideResult.profitability.estimated_profit_margin}</p>}

                                    {deploymentGuideResult.profitability.expected_expenses?.length > 0 && (
                                        <>
                                            <h5 className="font-semibold text-gray-700 mt-3 mb-1 text-sm">Expected Expenses</h5>
                                            <ul className="list-disc list-inside text-sm text-gray-600 space-y-1 pl-1">
                                                {deploymentGuideResult.profitability.expected_expenses.map((expense, index) => (
                                                    <li key={index}>{expense.name}: {expense.amount}</li>
                                                ))}
                                            </ul>
                                        </>
                                    )}
                                </div>
                            )}
                        </>
                    )}
                </div>
            )}
          </div>
        );
      default:
        return null;
    }
  };


  return (
    <div className="container mx-auto px-4 py-8 archon-container bg-gray-50 rounded-lg shadow-md my-8">
      {/* Header */}
      <div className="archon-header bg-gradient-to-r from-blue-600 to-blue-800 text-white p-6 text-center rounded-t-lg">
        <h2 className="text-3xl font-bold mb-2">Archon Passive Income Generator</h2>
        <p className="opacity-80">Create automated income streams with minimal human intervention</p>
      </div>

      {/* Content Area */}
      <div className="archon-content flex min-h-[500px]">
        {/* Sidebar */}
        <div className="archon-sidebar w-[300px] bg-gray-100 border-r border-gray-300 p-6">
          <div className="archon-section mb-8">
            <h3 className="text-xl font-semibold border-b border-gray-300 pb-2 mb-4">Income Streams</h3>
            <div id="income-streams-list" className="income-streams-list mb-4">
              {loading && <p>Loading streams...</p>}
              {error && <p className="text-red-600">{error}</p>}
              {!loading && !error && incomeStreams.length === 0 && (
                <p>No income streams created yet.</p>
              )}
              {!loading && !error && incomeStreams.map(stream => (
                <div
                  key={stream.id}
                  className={`income-stream-item p-3 bg-white rounded-md border border-gray-300 mb-2 cursor-pointer transition-all hover:border-blue-500 hover:shadow-sm ${selectedStream?.id === stream.id ? 'border-blue-500 shadow-md ring-2 ring-blue-200' : ''}`}
                  onClick={() => handleSelectStream(stream)}
                >
                  <h4 className="font-semibold text-sm mb-1">{stream.name}</h4>
                  <p className="text-xs text-gray-600 mb-2 truncate">{stream.description}</p>
                  <span className="income-stream-badge inline-block text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-600">{stream.type}</span>
                </div>
              ))}
            </div>
            <button
              id="new-income-stream-btn"
              className="btn btn-primary w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition"
              onClick={() => {
                  setShowForm(true);
                  setSelectedStream(null); // Deselect stream when showing form
              }}
            >
              Create New Income Stream
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="archon-main flex-1 p-6">
          {/* Income Stream Form (conditionally rendered) */}
          {showForm && (
            <div id="income-stream-form-container" className="archon-section mb-8">
              <h3 className="text-xl font-semibold border-b border-gray-300 pb-2 mb-4">Create Income Stream</h3>
              <form id="income-stream-form" onSubmit={handleCreateStreamSubmit}>
                 {formError && <p className="text-red-600 mb-4">{formError}</p>}
                <div className="input-group mb-5">
                  <label htmlFor="stream-name" className="block mb-1.5 font-medium text-sm text-gray-700">Name</label>
                  <input type="text" id="stream-name" name="name" value={formData.name} onChange={handleInputChange} className="form-input w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-300" placeholder="Name your income stream" required />
                </div>

                <div className="input-group mb-5">
                  <label htmlFor="stream-type" className="block mb-1.5 font-medium text-sm text-gray-700">Type</label>
                  <select id="stream-type" name="stream_type" value={formData.stream_type} onChange={handleInputChange} className="form-input w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white" required>
                    <option value="">Select a type</option>
                    <option value="membership">Membership Site</option>
                    <option value="digital_product">Digital Product</option>
                    <option value="affiliate">Affiliate Marketing</option>
                    <option value="saas">Software as a Service</option>
                    <option value="marketplace">Marketplace</option>
                  </select>
                </div>

                <div className="input-group mb-5">
                  <label htmlFor="stream-description" className="block mb-1.5 font-medium text-sm text-gray-700">Description</label>
                  <textarea id="stream-description" name="description" value={formData.description} onChange={handleInputChange} className="form-input w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-300" placeholder="Describe your income stream" required></textarea>
                </div>

                <div className="input-group mb-5">
                  <label htmlFor="automation-level" className="block mb-1.5 font-medium text-sm text-gray-700">Automation Level ({formData.automation_level}/10)</label>
                  <input type="range" id="automation-level" name="automation_level" value={formData.automation_level} onChange={handleInputChange} className="form-range w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700" min="1" max="10" />
                   {/* <div className="range-value text-center font-medium mt-2 text-sm"><span id="automation-value">{formData.automation_level}</span>/10</div> */}
                </div>

                <div className="input-group mb-5">
                  <label className="block mb-1.5 font-medium text-sm text-gray-700">Required Services</label>
                  <div className="checkbox-group flex flex-wrap gap-x-4 gap-y-2">
                    {['stripe', 'shopify', 'mailchimp', 'wordpress'].map(service => (
                       <label key={service} className="checkbox-label flex items-center cursor-pointer text-sm">
                         <input
                            type="checkbox"
                            name="required-services"
                            value={service}
                            checked={formData.required_services.includes(service)}
                            onChange={handleInputChange}
                            className="mr-1.5 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                         /> {service.charAt(0).toUpperCase() + service.slice(1)}
                       </label>
                    ))}
                  </div>
                </div>

                <div className="form-actions flex gap-4 mt-6">
                  <button type="submit" className="btn btn-primary bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition text-sm" disabled={isSubmitting}>
                    {isSubmitting ? 'Creating...' : 'Create Income Stream'}
                  </button>
                  <button type="button" id="cancel-form" className="btn btn-secondary bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 px-4 rounded transition text-sm" onClick={() => { setShowForm(false); setFormData(initialFormData); setFormError(null); }}>Cancel</button>
                </div>
              </form>
            </div>
          )}

          {/* Income Stream Details (conditionally rendered) */}
          {!showForm && selectedStream ? (
            <div id="income-stream-details" className="archon-section">
              {/* Header */}
              <div id="income-stream-header" className="mb-6">
                <h3 className="text-2xl font-bold flex items-center">
                  {selectedStream.name}
                  <span className="badge text-xs px-2.5 py-1 rounded-full bg-blue-100 text-blue-600 ml-3">{selectedStream.type}</span>
                </h3>
                <p className="text-gray-700 mt-1">{selectedStream.description}</p>
              </div>

              {/* Tabs */}
              <div className="archon-tabs flex border-b border-gray-300 mb-6">
                {['overview', 'implement', 'forecast', 'deploy'].map(tab => (
                  <button
                    key={tab}
                    className={`tab-btn px-5 py-2 text-sm capitalize transition-colors duration-150 ${activeTab === tab ? 'font-medium text-blue-600 border-b-2 border-blue-600' : 'text-gray-600 hover:text-blue-600'}`}
                    onClick={() => setActiveTab(tab)}
                  >
                    {tab === 'forecast' ? 'Revenue Forecast' : tab === 'deploy' ? 'Deployment Guide' : tab}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div className="tab-content">
                {renderTabContent()}
              </div>
            </div>
          ) : (
            !loading && !error && <p>Select an income stream to see details or create a new one.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default ArchonDashboard;