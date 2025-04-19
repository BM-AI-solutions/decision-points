import React, { useEffect, useState } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import apiService from '../services/api.js';
import '../../css/dashboard-full.css'; // Import the CSS file

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

function Dashboard() {
  const [businessModels, setBusinessModels] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [selectedBusinessId, setSelectedBusinessId] = useState(null);
  // Combined loading state removed, using specific loaders now
  const [error, setError] = useState('');
  const [loadingModels, setLoadingModels] = useState(true);
  const [loadingForecast, setLoadingForecast] = useState(false);

  // Effect to fetch business models on mount
  useEffect(() => {
    async function fetchModelsData() {
      setLoadingModels(true);
      setError('');
      try {
        const modelsRes = await apiService.getBusinessModels();
        const models = modelsRes?.business_models || [];
        setBusinessModels(models);

        if (models.length > 0) {
          // Set the initially selected model ID
          setSelectedBusinessId(models[0].id);
        } else {
          setSelectedBusinessId(null); // No models, clear selection
          setForecast(null); // Clear forecast if no models
        }
      } catch (err) {
        console.error("Dashboard: Error fetching business models:", err);
        setError('Failed to load business models.');
        setBusinessModels([]); // Clear models on error
        setSelectedBusinessId(null);
        setForecast(null); // Clear forecast on error
      } finally {
        setLoadingModels(false);
      }
    }
    fetchModelsData();
  }, []); // Empty dependency array ensures this runs only once on mount

  // Effect to fetch forecast data when selectedBusinessId changes
  useEffect(() => {
    if (!selectedBusinessId) {
      setForecast(null); // Clear forecast if no model is selected
      return;
    }

    async function fetchForecastData() {
      setLoadingForecast(true);
      // Clear only forecast-related errors, keep model fetch errors if they occurred
      // setError(''); // Let's not clear general errors here
      try {
        const forecastRes = await apiService.getCashflowForecast(selectedBusinessId);
        setForecast(forecastRes?.forecast || null);
        setError(''); // Clear error *after* successful forecast fetch
      } catch (err) {
        console.error(`Dashboard: Error fetching forecast for ${selectedBusinessId}:`, err);
        setError(`Failed to load forecast data for the selected model.`); // Set specific error
        setForecast(null); // Clear forecast on error
      } finally {
        setLoadingForecast(false);
      }
    }

    fetchForecastData();
  }, [selectedBusinessId]); // Dependency array includes selectedBusinessId

  // Prepare chart data
  const monthlyLabels = forecast?.monthly?.map(m => m.month) || [];
  const monthlyRevenue = forecast?.monthly?.map(m => m.revenue) || [];

  const growthRate = forecast?.growth_rate ?? 0;
  const customerLabels = monthlyLabels;
  const baseCustomers = 40; // Assuming this is static or fetched elsewhere
  const customerGrowth = monthlyLabels.map((_, i) =>
    Math.round(baseCustomers * Math.pow(1 + growthRate, i))
  );

  // AI Insights (ensure this is correct)
  const aiInsights = [
    {
      icon: 'fas fa-arrow-up',
      text: forecast
        ? `Revenue increased by ${Math.round(growthRate * 100)}% this month`
        : 'Data unavailable',
    },
    {
      icon: 'fas fa-users',
      text: forecast
        ? `Customer growth rate: ${(growthRate * 100).toFixed(1)}%`
        : 'Data unavailable',
    },
    {
      icon: 'fas fa-lightbulb',
      text: 'New market opportunity detected', // This seems static
    },
  ];

  // Loading state for initial models fetch
  if (loadingModels) {
    return (
      <div className="dashboard-loading">
        <span>Loading business models...</span>
      </div>
    );
  }

  // Error state primarily for models fetch error, forecast errors handled differently
  // Show general error only if models failed to load and we aren't loading forecast
  if (error && !selectedBusinessId && !loadingForecast) {
    return (
      <div className="dashboard-error">
        <span>{error}</span>
      </div>
    );
  }

  // Main dashboard content
  return (
    <div className="dashboard-grid">
      {/* Business Model Selector */}
      {businessModels.length > 1 && ( // Only show selector if more than one model
        <div className="dashboard-model-selector" style={{ gridColumn: '1 / 4', marginBottom: '-10px' }}> {/* Basic styling */}
          <label htmlFor="businessModelSelect" style={{ marginRight: '10px', color: 'var(--text-secondary)' }}>Select Business Model:</label>
          <select
            id="businessModelSelect"
            value={selectedBusinessId || ''}
            onChange={(e) => setSelectedBusinessId(e.target.value)}
            disabled={loadingForecast || loadingModels} // Disable while loading either
            style={{ padding: '5px 8px', borderRadius: '4px', background: 'var(--background-secondary)', color: 'var(--text-primary)', border: '1px solid var(--border-color)' }}
          >
            {businessModels.map(model => (
              <option key={model.id} value={model.id}>
                {model.name || `Model ${model.id}`} {/* Display name or ID */}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Display loading/error specific to forecast */}
      {loadingForecast && (
        <div className="dashboard-loading" style={{ gridColumn: '1 / 4' }}>
          <span>Loading forecast data...</span>
        </div>
      )}
      {/* Show forecast-specific error if it occurred */}
      {error && !loadingForecast && selectedBusinessId && error.includes('forecast data') && (
         <div className="dashboard-error" style={{ gridColumn: '1 / 4' }}>
           <span>{error}</span>
         </div>
      )}

      {/* Render charts and insights only if a model is selected and forecast isn't loading and there's no forecast error */}
      {selectedBusinessId && !loadingForecast && !(error && error.includes('forecast data')) ? (
        <>
          {forecast ? (
            <>
              {/* Monthly Revenue Chart - Spans 2 columns */}
              <div className="dashboard-card dashboard-card-revenue">
                 <h4 className="dashboard-card-title">Monthly Revenue</h4>
                 <div className="dashboard-chart-container">
                   <Line
                     data={{
                       labels: monthlyLabels,
                       datasets: [
                         {
                           label: 'Revenue',
                           data: monthlyRevenue,
                           borderColor: '#3b82f6',
                           backgroundColor: 'rgba(59, 130, 246, 0.1)',
                           fill: true,
                           tension: 0.4,
                           pointBackgroundColor: '#3b82f6',
                           pointBorderColor: '#fff',
                           pointBorderWidth: 2,
                           pointRadius: 3,
                           pointHoverRadius: 5,
                         },
                       ],
                     }}
                     options={{
                       responsive: true,
                       maintainAspectRatio: false,
                       plugins: {
                         legend: {
                           display: false
                         }
                       },
                       scales: {
                         x: {
                           grid: {
                             display: false
                           },
                           ticks: {
                             color: 'rgba(255, 255, 255, 0.7)',
                             font: {
                               size: 10
                             }
                           }
                         },
                         y: {
                           grid: {
                             color: 'rgba(255, 255, 255, 0.1)'
                           },
                           ticks: {
                             color: 'rgba(255, 255, 255, 0.7)',
                             font: {
                               size: 10
                             },
                             callback: function(value) {
                               return '$' + value;
                             }
                           }
                         }
                       }
                     }}
                   />
                 </div>
               </div>

              {/* Customer Growth Chart */}
              <div className="dashboard-card dashboard-card-customer">
                 <h4 className="dashboard-card-title">Customer Growth</h4>
                 <div className="dashboard-chart-container-bar">
                   <Bar
                     data={{
                       labels: customerLabels,
                       datasets: [
                         {
                           label: 'New Customers',
                           data: customerGrowth,
                           backgroundColor: 'rgba(59, 130, 246, 0.7)',
                           borderColor: '#3b82f6',
                           borderWidth: 1,
                           borderRadius: 4,
                         },
                       ],
                     }}
                     options={{
                       responsive: true,
                       maintainAspectRatio: false,
                       plugins: {
                         legend: {
                           display: false
                         }
                       },
                       scales: {
                         x: {
                           grid: {
                             display: false
                           },
                           ticks: {
                             color: 'rgba(255, 255, 255, 0.7)',
                             font: {
                               size: 10
                             }
                           }
                         },
                         y: {
                           grid: {
                             color: 'rgba(255, 255, 255, 0.1)'
                           },
                           ticks: {
                             color: 'rgba(255, 255, 255, 0.7)',
                             font: {
                               size: 10
                             }
                           }
                         }
                       }
                     }}
                   />
                 </div>
               </div>

              {/* AI Insights */}
              <div className="dashboard-card dashboard-card-insights">
                 <h4 className="dashboard-card-title">AI Insights</h4>
                 <div className="dashboard-insights-list">
                   {aiInsights.map((insight, idx) => (
                     <div key={idx} className="dashboard-insight-item">
                       <div className="dashboard-insight-icon-wrapper">
                         <i className={`${insight.icon} dashboard-insight-icon`}></i>
                       </div>
                       <span className="dashboard-insight-text">{insight.text}</span>
                     </div>
                   ))}
                 </div>
               </div>
            </>
          ) : (
             // Render message if forecast is null but no error occurred for it
             <div className="dashboard-no-data" style={{ gridColumn: '1 / 4' }}>
               <h3 className="dashboard-no-data-title">No Forecast Data</h3>
               <p>Forecast data could not be loaded or is unavailable for this model.</p>
             </div>
          )}
        </>
      ) : (!loadingModels && businessModels.length === 0 &&
          // Render 'No Business Models Found' only if models finished loading and there are none
          <div className="dashboard-no-data">
            <h3 className="dashboard-no-data-title">No Business Models Found</h3>
            <p>Create a business model to see dashboard data and insights.</p>
          </div>
      )}
    </div>
  );
}

export default Dashboard;