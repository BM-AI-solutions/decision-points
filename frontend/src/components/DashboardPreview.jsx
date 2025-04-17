import React from 'react';

function DashboardPreview() {
  return (
    <section className="dashboard-preview">
      <div className="container">
        <div className="dashboard-content animate-on-scroll">
          <h2>Ease of Use with a Powerful <span className="accent-text">Dashboard</span></h2>
          <p>Manage and automate your business with an intuitive and powerful dashboard.</p>
          
          <ul className="dashboard-features">
            <li><i className="fas fa-check"></i> Real-time analytics and reporting</li>
            <li><i className="fas fa-check"></i> Automated business processes</li>
            <li><i className="fas fa-check"></i> Customizable widgets and modules</li>
            <li><i className="fas fa-check"></i> Integrated AI-powered insights</li>
          </ul>
        </div>
        
        <div className="dashboard-image animate-on-scroll">
          <img src="images/hero-image.svg" alt="Dashboard Preview" />
        </div>
      </div>
    </section>
  );
}

export default DashboardPreview;