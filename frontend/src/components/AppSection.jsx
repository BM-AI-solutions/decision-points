import React from 'react';

function AppSection() {
  return (
    <section id="app" className="app-section">
      <div className="container">
        <div className="app-content">
          <div className="section-header">
            <h2>Start Building Your <span className="accent-text">Business Empire</span></h2>
            <p>Analyze a market segment and begin your automated business journey</p>
          </div>
          <div className="app-interface">
            <div className="market-analysis-form">
              <div className="input-group">
                <label htmlFor="market-segment">Market Segment</label>
                <select id="market-segment" className="form-input">
                  <option value="">Select a market segment</option>
                  <option value="digital-products">Digital Products</option>
                  <option value="e-commerce">E-Commerce</option>
                  <option value="saas">SaaS</option>
                  <option value="online-education">Online Education</option>
                  <option value="affiliate-marketing">Affiliate Marketing</option>
                </select>
              </div>
              <div className="input-group">
                <label htmlFor="business-preference">Business Preference</label>
                <select id="business-preference" className="form-input">
                  <option value="">Select your preference</option>
                  <option value="highest-revenue">Highest Revenue Potential</option>
                  <option value="lowest-effort">Lowest Human Effort</option>
                  <option value="fastest-implementation">Fastest Implementation</option>
                  <option value="lowest-startup-cost">Lowest Startup Cost</option>
                </select>
              </div>
              <button id="analyze-btn" className="btn btn-primary btn-large">Analyze Market <i className="fas fa-arrow-right"></i></button>
            </div>
            <div className="analysis-results hidden">
              <div className="results-header">
                <h3>Market Analysis Results</h3>
                <span className="badge">3 Business Models Found</span>
              </div>
              <div className="business-models">
                {/* Business models will be dynamically added here */}
                Business models will be dynamically added here
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default AppSection;