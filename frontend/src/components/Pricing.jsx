import React, { useState } from 'react';

function Pricing() {
  const [isYearly, setIsYearly] = useState(false);

  const starterMonthlyPrice = 49;
  const enterpriseMonthlyPrice = 149;

  const starterYearlyPrice = Math.round(starterMonthlyPrice * 0.8 * 12); // Calculate yearly total with discount
  const enterpriseYearlyPrice = Math.round(enterpriseMonthlyPrice * 0.8 * 12); // Calculate yearly total with discount

  const togglePricing = () => {
    setIsYearly(!isYearly);
  };

  return (
    <section id="pricing" className="pricing-section">
      <div className="container">
        <div className="section-header animate-on-scroll">
          <h2>Choose Your <span className="accent-text">Plan</span></h2>
          <p>Preferential pricing for startups, growing businesses, and large enterprises</p>
        </div>

        {/* Pricing Toggle Switch */}
        <div className="pricing-toggle-container animate-on-scroll">
          <span>Monthly</span>
          <label className="pricing-toggle switch">
            <input type="checkbox" checked={isYearly} onChange={togglePricing} />
            <span className="slider round"></span>
          </label>
          <span>Yearly <span className="save-badge">Save 20%</span></span>
        </div>

        <div className="pricing-cards">
          {/* Free Plan Card (No price change) */}
          <div className="pricing-card animate-on-scroll">
            <div className="pricing-header">
              <h3>Free Plan</h3>
              <div className="price">
                <span className="currency">$</span>
                <span className="amount">0</span>
                <span className="period">/mo</span>
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

          {/* Starter Plan Card */}
          <div className="pricing-card featured animate-on-scroll">
            <div className="popular-badge">Most Popular</div>
            <div className="pricing-header">
              <h3>Starter Plan</h3>
              <div className="price">
                <span className="currency">$</span>
                <span className="amount">{isYearly ? Math.round(starterYearlyPrice / 12) : starterMonthlyPrice}</span>
                <span className="period">{isYearly ? '/mo (billed annually)' : '/mo'}</span>
              </div>
              {isYearly && <div className="yearly-total">Total ${starterYearlyPrice}/yr</div>}
            </div>
            <ul className="pricing-features">
              <li><i className="fas fa-check"></i> Enhanced Market Analysis</li>
              <li><i className="fas fa-check"></i> 5 Business Models</li>
              <li><i className="fas fa-check"></i> Advanced Analytics</li>
              <li><i className="fas fa-check"></i> Premium Features</li>
            </ul>
            <button className="btn btn-primary ember-glow">Choose Starter</button>
          </div>

          {/* Enterprise Plan Card */}
          <div className="pricing-card animate-on-scroll">
            <div className="pricing-header">
              <h3>Enterprise Plan</h3>
              <div className="price">
                <span className="currency">$</span>
                <span className="amount">{isYearly ? Math.round(enterpriseYearlyPrice / 12) : enterpriseMonthlyPrice}</span>
                <span className="period">{isYearly ? '/mo (billed annually)' : '/mo'}</span>
              </div>
              {isYearly && <div className="yearly-total">Total ${enterpriseYearlyPrice}/yr</div>}
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