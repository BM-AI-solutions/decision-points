import React, { useState } from 'react';

function AppSection() {
  const [marketSegment, setMarketSegment] = useState('');
  const [businessPreference, setBusinessPreference] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);

  const handleMarketSegmentChange = (event) => {
    setMarketSegment(event.target.value);
  };

  const handleBusinessPreferenceChange = (event) => {
    setBusinessPreference(event.target.value);
  };

  const handleAnalyzeMarket = () => {
    // For now, just display the selected values
    setAnalysisResults({
      marketSegment: marketSegment || 'Not selected',
      businessPreference: businessPreference || 'Not selected',
      message: 'Analysis results would be displayed here.'
    });
  };

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
                <select
                  id="market-segment"
                  className="form-input"
                  value={marketSegment}
                  onChange={handleMarketSegmentChange}
                >
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
                <select
                  id="business-preference"
                  className="form-input"
                  value={businessPreference}
                  onChange={handleBusinessPreferenceChange}
                >
                  <option value="">Select your preference</option>
                  <option value="highest-revenue">Highest Revenue Potential</option>
                  <option value="lowest-effort">Lowest Human Effort</option>
                  <option value="fastest-implementation">Fastest Implementation</option>
                  <option value="lowest-startup-cost">Lowest Startup Cost</option>
                </select>
              </div>
              <button
                id="analyze-btn"
                className="btn btn-primary btn-large"
                onClick={handleAnalyzeMarket}
              >
                Analyze Market <i className="fas fa-arrow-right"></i>
              </button>
            </div>
            {analysisResults && (
              <div className="analysis-results">
                <div className="results-header">
                  <h3>Market Analysis Results</h3>
                  {/* <span className="badge">3 Business Models Found</span> Placeholder for future */}
                </div>
                <div className="business-models">
                  <p><strong>Market Segment:</strong> {analysisResults.marketSegment}</p>
                  <p><strong>Business Preference:</strong> {analysisResults.businessPreference}</p>
                  <p>{analysisResults.message}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

export default AppSection;