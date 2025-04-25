import React from 'react';

function DashboardPreview() {
  return (
    <section className="dashboard-preview">
      <div className="container">
        <div className="preview-content">
          <div className="preview-description">
            <h2>Ease of Use with a Powerful <span className="accent-text">Dashboard</span></h2>
            <p>Manage and automate your business with an intuitive and powerful dashboard.</p>
          </div>
          <div className="preview-image">
            <img src="images/hero-image.svg" alt="Dashboard Preview" />
          </div>
        </div>
      </div>
    </section>
  );
}

export default DashboardPreview;