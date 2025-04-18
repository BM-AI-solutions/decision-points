import React, { useEffect, useState } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import apiService from '../services/api.js';
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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError('');
      try {
        console.log("Dashboard: Fetching business models");
        const modelsRes = await apiService.getBusinessModels();
        console.log("Dashboard: Business models response:", modelsRes);
        const models = modelsRes?.business_models || [];
        console.log("Dashboard: Extracted models:", models);
        setBusinessModels(models);

        if (models.length > 0) {
          const businessId = models[0].id;
          console.log("Dashboard: Fetching forecast for business ID:", businessId);
          const forecastRes = await apiService.getCashflowForecast(businessId);
          console.log("Dashboard: Forecast response:", forecastRes);
          setForecast(forecastRes?.forecast || null);
        } else {
          console.log("Dashboard: No business models found, skipping forecast");
          setForecast(null);
        }
      } catch (err) {
        console.error("Dashboard: Error fetching data:", err);
        setError('Failed to load dashboard data.');
        setForecast(null);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // Prepare chart data
  const monthlyLabels = forecast?.monthly?.map(m => m.month) || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
  const monthlyRevenue = forecast?.monthly?.map(m => m.revenue) || [4200, 5100, 5800, 6300, 7100, 7800];

  const growthRate = forecast?.growth_rate ?? 0.15;
  const customerLabels = monthlyLabels;
  const baseCustomers = 40;
  const customerGrowth = monthlyLabels.map((_, i) =>
    Math.round(baseCustomers * Math.pow(1 + growthRate, i))
  );

  // AI Insights
  const aiInsights = [
    {
      icon: 'fas fa-arrow-up',
      text: forecast
        ? `Revenue increased by ${Math.round(growthRate * 100)}% this month`
        : 'Revenue increased by 24% this month',
    },
    {
      icon: 'fas fa-users',
      text: forecast
        ? `Customer growth rate: ${(growthRate * 100).toFixed(1)}%`
        : 'Customer retention improved to 87%',
    },
    {
      icon: 'fas fa-lightbulb',
      text: 'New market opportunity detected',
    },
  ];

  // Loading state
  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#fff' }}>
        <span>Loading dashboard data...</span>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#ff4713' }}>
        <span>{error}</span>
      </div>
    );
  }

  // Main dashboard content
  return (
    <div style={{
      padding: '20px',
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gridTemplateRows: 'auto auto',
      gap: '20px',
      height: '100%',
      overflow: 'auto'
    }}>
      {businessModels.length > 0 && forecast ? (
        <>
          {/* Monthly Revenue Chart - Spans 2 columns */}
          <div style={{
            gridColumn: '1 / 3',
            background: 'rgba(13, 13, 13, 0.7)',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
            border: '1px solid rgba(59, 130, 246, 0.2)'
          }}>
            <h4 style={{ 
              marginBottom: '15px', 
              fontSize: '16px', 
              fontWeight: '600',
              color: '#fff'
            }}>Monthly Revenue</h4>
            <div style={{ height: '220px' }}>
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
          <div style={{
            gridColumn: '3 / 4',
            background: 'rgba(13, 13, 13, 0.7)',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
            border: '1px solid rgba(59, 130, 246, 0.2)'
          }}>
            <h4 style={{ 
              marginBottom: '15px', 
              fontSize: '16px', 
              fontWeight: '600',
              color: '#fff'
            }}>Customer Growth</h4>
            <div style={{
              height: '220px',
              position: 'relative',
              zIndex: 1
            }}>
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
          <div style={{
            gridColumn: '1 / 4',
            background: 'rgba(13, 13, 13, 0.7)',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
            border: '1px solid rgba(59, 130, 246, 0.2)'
          }}>
            <h4 style={{ 
              marginBottom: '15px', 
              fontSize: '16px', 
              fontWeight: '600',
              color: '#fff'
            }}>AI Insights</h4>
            <div style={{ 
              display: 'flex', 
              flexWrap: 'wrap',
              gap: '15px' 
            }}>
              {aiInsights.map((insight, idx) => (
                <div key={idx} style={{
                  flex: '1',
                  minWidth: '200px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '15px',
                  background: 'rgba(30, 0, 0, 0.5)',
                  borderRadius: '8px',
                  fontSize: '14px'
                }}>
                  <div style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '50%',
                    background: 'rgba(255, 71, 19, 0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <i className={insight.icon} style={{ 
                      color: '#ff4713',
                      fontSize: '16px'
                    }}></i>
                  </div>
                  <span style={{ color: '#fff' }}>{insight.text}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : (
        <div style={{ 
          gridColumn: '1 / 4',
          padding: '40px', 
          textAlign: 'center', 
          color: 'var(--text-secondary)',
          background: 'rgba(13, 13, 13, 0.7)',
          borderRadius: '12px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
        }}>
          <h3 style={{ marginBottom: '10px' }}>No Business Models Found</h3>
          <p>Create a business model to see dashboard data and insights.</p>
        </div>
      )}
    </div>
  );
}

export default Dashboard;