import React, { useEffect, useState } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api.js';

function Dashboard() {
  const [businessModels, setBusinessModels] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

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
      }
      setLoading(false);
    }
    fetchData();
  }, []);

  // Prepare chart data
  const monthlyLabels = forecast?.monthly?.map(m => m.month) || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
  const monthlyRevenue = forecast?.monthly?.map(m => m.revenue) || [4200, 5100, 5800, 6300, 7100, 7800];

  // For customer growth, use growth_rate as a proxy (mocked if not available)
  const growthRate = forecast?.growth_rate ?? 0.15;
  const customerLabels = monthlyLabels;
  // Mock customer growth based on growth rate
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

  // Sidebar navigation handlers
  const sidebarLinks = [
    { label: 'Dashboard', icon: 'fas fa-home', route: '/dashboard' },
    { label: 'Analytics', icon: 'fas fa-chart-pie', route: '/analytics' },
    { label: 'Automation', icon: 'fas fa-cogs', route: '/automation' },
    { label: 'Insights', icon: 'fas fa-lightbulb', route: '/insights' },
    { label: 'Customers', icon: 'fas fa-users', route: '/customers' },
    { label: 'Revenue', icon: 'fas fa-dollar-sign', route: '/revenue' },
  ];

  return (
    <section className="dashboard-full">
      <div className="dashboard-container">
        <div className="dashboard-content animate-on-scroll">
          <h2>
            Ease of Use with a Powerful <span className="accent-text">Dashboard</span>
          </h2>
          <p>Manage and automate your business with an intuitive and powerful dashboard.</p>

          <ul className="dashboard-features">
            <li>
              <i className="fas fa-chart-line"></i> Real-time analytics and reporting
            </li>
            <li>
              <i className="fas fa-robot"></i> Automated business processes
            </li>
            <li>
              <i className="fas fa-th-large"></i> Customizable widgets and modules
            </li>
            <li>
              <i className="fas fa-brain"></i> Integrated AI-powered insights
            </li>
            <li>
              <i className="fas fa-bolt"></i> Lightning-fast performance
            </li>
          </ul>

          <button className="btn btn-primary ember-glow">
            Explore Dashboard <i className="fas fa-arrow-right"></i>
          </button>
        </div>

        <div className="dashboard-image animate-on-scroll">
          <div className="dashboard-mockup">
            <div className="dashboard-header">
              <div className="dashboard-logo">
                <i className="fas fa-fire"></i> Decision Points AI
              </div>
              <div className="dashboard-controls">
                <i className="fas fa-bell"></i>
                <i className="fas fa-cog"></i>
                <i className="fas fa-user-circle"></i>
              </div>
            </div>
            <div className="dashboard-content-area">
              <div className="dashboard-sidebar">
                {sidebarLinks.map((link, idx) => (
                  <div
                    key={link.label}
                    className={`sidebar-item${idx === 0 ? ' active' : ''}`}
                    onClick={() => navigate(link.route)}
                    style={{ cursor: 'pointer' }}
                  >
                    <i className={link.icon}></i> {link.label}
                  </div>
                ))}
              </div>
              <div className="dashboard-main">
                <div className="dashboard-widget revenue">
                  <h4>Monthly Revenue</h4>
                  <div className="chart-container">
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
                            pointRadius: 2,
                            pointHoverRadius: 4,
                          },
                        ],
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            display: false,
                          },
                          tooltip: {
                            callbacks: {
                              label: function (context) {
                                return `$${context.raw}`;
                              },
                            },
                          },
                        },
                        scales: {
                          x: {
                            display: true,
                            grid: {
                              display: false,
                            },
                            ticks: {
                              font: {
                                size: 9,
                              },
                              maxTicksLimit: 3,
                            },
                          },
                          y: {
                            display: true,
                            grid: {
                              color: 'rgba(0, 0, 0, 0.05)',
                            },
                            ticks: {
                              callback: function (value) {
                                return '$' + value;
                              },
                              font: {
                                size: 9,
                              },
                              maxTicksLimit: 3,
                            },
                          },
                        },
                      }}
                    />
                  </div>
                </div>
                <div className="dashboard-widget customers">
                  <h4>Customer Growth</h4>
                  <div className="chart-container">
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
                            borderRadius: 2,
                          },
                        ],
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            display: false,
                          },
                        },
                        scales: {
                          x: {
                            display: true,
                            grid: {
                              display: false,
                            },
                            ticks: {
                              font: {
                                size: 9,
                              },
                              maxTicksLimit: 3,
                            },
                          },
                          y: {
                            display: true,
                            grid: {
                              color: 'rgba(0, 0, 0, 0.05)',
                            },
                            ticks: {
                              font: {
                                size: 9,
                              },
                              maxTicksLimit: 3,
                            },
                          },
                        },
                      }}
                    />
                  </div>
                </div>
                <div className="dashboard-widget insights">
                  <h4>AI Insights</h4>
                  <div className="insights-list">
                    {aiInsights.map((insight, idx) => (
                      <div className="insight-item" key={idx}>
                        <i className={insight.icon}></i>
                        <span>{insight.text}</span>
                      </div>
                    ))}
                  </div>
                </div>
                {loading && (
                  <div className="dashboard-loading">
                    <span>Loading dashboard data...</span>
                  </div>
                )}
                {error && (
                  <div className="dashboard-error">
                    <span>{error}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Dashboard;