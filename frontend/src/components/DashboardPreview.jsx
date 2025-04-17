import React from 'react';
import { Line, Bar } from 'react-chartjs-2';

function DashboardPreview() {
  return (
    <section className="dashboard-preview">
      <div className="container">
        <div className="dashboard-content animate-on-scroll">
          <h2>Ease of Use with a Powerful <span className="accent-text">Dashboard</span></h2>
          <p>Manage and automate your business with an intuitive and powerful dashboard.</p>
          
          <ul className="dashboard-features">
            <li><i className="fas fa-chart-line"></i> Real-time analytics and reporting</li>
            <li><i className="fas fa-robot"></i> Automated business processes</li>
            <li><i className="fas fa-th-large"></i> Customizable widgets and modules</li>
            <li><i className="fas fa-brain"></i> Integrated AI-powered insights</li>
            <li><i className="fas fa-bolt"></i> Lightning-fast performance</li>
          </ul>
          
          <button className="btn btn-primary ember-glow">Explore Dashboard <i className="fas fa-arrow-right"></i></button>
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
                <div className="sidebar-item active"><i className="fas fa-home"></i> Dashboard</div>
                <div className="sidebar-item"><i className="fas fa-chart-pie"></i> Analytics</div>
                <div className="sidebar-item"><i className="fas fa-cogs"></i> Automation</div>
                <div className="sidebar-item"><i className="fas fa-lightbulb"></i> Insights</div>
                <div className="sidebar-item"><i className="fas fa-users"></i> Customers</div>
                <div className="sidebar-item"><i className="fas fa-dollar-sign"></i> Revenue</div>
              </div>
              <div className="dashboard-main">
                <div className="dashboard-widget revenue">
                  <h4>Monthly Revenue</h4>
                  <div style={{ height: '120px' }}>
                    <Line
                      data={{
                        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                        datasets: [
                          {
                            label: 'Revenue',
                            data: [4200, 5100, 5800, 6300, 7100, 7800],
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            fill: true,
                            tension: 0.4,
                            pointBackgroundColor: '#3b82f6',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2,
                            pointRadius: 3,
                            pointHoverRadius: 5
                          }
                        ]
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            display: false
                          },
                          tooltip: {
                            callbacks: {
                              label: function(context) {
                                return `$${context.raw}`;
                              }
                            }
                          }
                        },
                        scales: {
                          x: {
                            display: true,
                            grid: {
                              display: false
                            },
                            ticks: {
                              font: {
                                size: 10
                              }
                            }
                          },
                          y: {
                            display: true,
                            grid: {
                              color: 'rgba(0, 0, 0, 0.05)'
                            },
                            ticks: {
                              callback: function(value) {
                                return '$' + value;
                              },
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
                <div className="dashboard-widget customers">
                  <h4>Customer Growth</h4>
                  <div style={{ height: '120px' }}>
                    <Bar
                      data={{
                        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                        datasets: [
                          {
                            label: 'New Customers',
                            data: [45, 52, 68, 74, 83, 95],
                            backgroundColor: 'rgba(59, 130, 246, 0.7)',
                            borderColor: '#3b82f6',
                            borderWidth: 1,
                            borderRadius: 3
                          }
                        ]
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
                            display: true,
                            grid: {
                              display: false
                            },
                            ticks: {
                              font: {
                                size: 10
                              }
                            }
                          },
                          y: {
                            display: true,
                            grid: {
                              color: 'rgba(0, 0, 0, 0.05)'
                            },
                            ticks: {
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
                <div className="dashboard-widget insights">
                  <h4>AI Insights</h4>
                  <div className="insights-list">
                    <div className="insight-item">
                      <i className="fas fa-arrow-up"></i>
                      <span>Revenue increased by 24% this month</span>
                    </div>
                    <div className="insight-item">
                      <i className="fas fa-users"></i>
                      <span>Customer retention improved to 87%</span>
                    </div>
                    <div className="insight-item">
                      <i className="fas fa-lightbulb"></i>
                      <span>New market opportunity detected</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default DashboardPreview;