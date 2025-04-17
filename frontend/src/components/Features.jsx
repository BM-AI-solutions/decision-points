import React from 'react';

function Features() {
  return (
    <section id="features" className="features-section">
      <div className="container">
        <div className="section-header">
          <h2>Discover the <span className="accent-text">Key Features</span></h2>
          <p>Decision Points AI offers a suite of powerful tools to optimize your business strategy</p>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <i className="fas fa-chart-line"></i>
            <h3>Market Analysis</h3>
            <p>Advanced analytics to identify high-potential market segments.</p>
          </div>
          <div className="feature-card">
            <i className="fas fa-cogs"></i>
            <h3>Business Model Generation</h3>
            <p>Create automated business models tailored to your needs.</p>
          </div>
          <div className="feature-card">
            <i className="fas fa-code"></i>
            <h3>Automation Tools</h3>
            <p>Automate features to drive revenue with minimal effort.</p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Features;