import React from 'react';

function Pricing() {
  return (
    <section id="pricing" className="pricing-section">
      <div className="container">
        <div className="section-header">
          <h2>Choose Your <span className="accent-text">Plan</span></h2>
          <p>Preferential pricing for startups, growing businesses, and large enterprises</p>
        </div>
        <div className="pricing-table">
          <div className="pricing-card free">
            <div className="card-header">
              <h3>Free Plan</h3>
              <div className="price-info">
                <div className="price">$0</div>
                <div className="term">per month</div>
              </div>
            </div>
            <ul className="pricing-features">
              <li><i className="fas fa-check"></i> Basic Market Analysis</li>
              <li><i className="fas fa-check"></i> 1 Business Model</li>
              <li><i className="fas fa-check"></i> Basic Analytics</li>
              <li><i className="fas fa-check"></i> Limited Features</li>
            </ul>
            <button className="btn btn-outline-primary">Get Started</button>
          </div>
          <div className="pricing-card starter">
            <div className="card-header">
              <div className="best-value">Best Value</div>
              <h3>Starter Plan</h3>
              <div className="price-info">
                <div className="price">$49</div>
                <div className="term">per month</div>
              </div>
            </div>
            <ul className="pricing-features">
              <li><i className="fas fa-check"></i> Enhanced Market Analysis</li>
              <li><i className="fas fa-check"></i> 5 Business Models</li>
              <li><i className="fas fa-check"></i> Advanced Analytics</li>
              <li><i className="fas fa-check"></i> Premium Features</li>
            </ul>
            <button className="btn btn-primary">Choose Starter</button>
          </div>
          <div className="pricing-card enterprise">
            <div className="card-header">
              <h3>Enterprise Plan</h3>
              <div className="price-info">
                <div className="price">$149</div>
                <div className="term">per month</div>
              </div>
            </div>
            <ul className="pricing-features">
              <li><i className="fas fa-check"></i> Unlimited Business Models</li>
              <li><i className="fas fa-check"></i> Premium Market Analysis</li>
              <li><i className="fas fa-check"></i> Unlimited Revenue Features</li>
              <li><i className="fas fa-check"></i> Custom Branding</li>
              <li><i className="fas fa-check"></i> 24/7 Priority Support</li>
              <li><i className="fas fa-check"></i> Advanced Analytics</li>
              <li><i className="fas fa-check"></i> Custom Integrations</li>
            </ul>
            <button className="btn btn-outline-primary">Contact Sales</button>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Pricing;