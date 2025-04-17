import React, { useState, useRef } from 'react';
import apiService from '../services/api.js'; // Import the API service

// Helper function (can be moved to utils later) - REMOVED
/*
function generateBusinessModels(marketSegment, preference) {
  const models = [];
  let count = Math.floor(Math.random() * 2) + 2; // 2-3 models

  const modelTypes = {
      'digital-products': ['Membership Site', 'Digital Course Platform', 'Template Marketplace', 'eBook Publishing'],
      'e-commerce': ['Dropshipping Store', 'Print on Demand', 'Subscription Box', 'Niche Marketplace'],
      'saas': ['Productivity Tool', 'Marketing Automation', 'Analytics Platform', 'Customer Support System'],
      'online-education': ['Cohort-Based Course', 'On-Demand Training', 'Expert Community', 'Certification Program'],
      'affiliate-marketing': ['Review Website', 'Comparison Platform', 'Deal Aggregator', 'Niche Content Hub']
  };

  const preferenceData = {
      'highest-revenue': { revenueFactor: 1.5, implementationFactor: 0.8 },
      'lowest-effort': { revenueFactor: 0.8, implementationFactor: 1.5 },
      'fastest-implementation': { revenueFactor: 0.7, implementationFactor: 1.7 },
      'lowest-startup-cost': { revenueFactor: 0.6, implementationFactor: 1.2 }
  };

  const availableModels = modelTypes[marketSegment] || modelTypes['digital-products'];
  const factors = preferenceData[preference] || preferenceData['highest-revenue'];

  for (let i = 0; i < count; i++) {
      if (i < availableModels.length) {
          const baseRevenue = Math.floor(Math.random() * 3000) + 1000;
          const adjustedRevenue = Math.floor(baseRevenue * factors.revenueFactor);
          const implementation = Math.floor(Math.random() * 3) + 6;
          const automation = Math.floor(Math.random() * 3) + 7;

          models.push({
              name: availableModels[i],
              revenue: adjustedRevenue,
              implementation: implementation,
              automation: automation,
              description: getDescription(availableModels[i])
          });
      }
  }

  if (preference === 'highest-revenue') {
      models.sort((a, b) => b.revenue - a.revenue);
  }

  return models;
}

function getDescription(modelType) {
  const descriptions = {
      'Membership Site': 'Recurring membership site with premium digital content and tiered access levels.',
      'Digital Course Platform': 'Educational platform with automated course delivery and student management.',
      'Template Marketplace': 'Marketplace selling digital templates with instant delivery and no inventory.',
      'eBook Publishing': 'Digital publishing platform with automated delivery and marketing.',
      'Dropshipping Store': 'E-commerce store with products shipped directly from suppliers to customers.',
      'Print on Demand': 'Custom product store with items printed and shipped as orders come in.',
      'Subscription Box': 'Recurring delivery service with curated products sent monthly to subscribers.',
      'Niche Marketplace': 'Specialized marketplace connecting buyers and sellers in a specific niche.',
      'Productivity Tool': 'SaaS solution that helps businesses improve workflow efficiency.',
      'Marketing Automation': 'Platform that automates repetitive marketing tasks and campaigns.',
      'Analytics Platform': 'Data analysis tool that provides actionable business insights.',
      'Customer Support System': 'Automated customer service solution with ticketing and knowledge base.',
      'Cohort-Based Course': 'Time-limited learning program where students progress together as a group.',
      'On-Demand Training': 'Self-paced educational content available 24/7 to subscribers.',
      'Expert Community': 'Paid membership community with access to industry experts and peers.',
      'Certification Program': 'Educational system that provides verified credentials upon completion.',
      'Review Website': 'Content site monetized through affiliate commissions from reviewed products.',
      'Comparison Platform': 'Website that compares similar products and earns commissions on referrals.',
      'Deal Aggregator': 'Platform that collects and displays the best deals with affiliate links.',
      'Niche Content Hub': 'Specialized content website with in-depth articles and affiliate promotions.'
  };
  return descriptions[modelType] || 'A business model with automation and passive income potential.';
}
*/

// Business Model Card Component
function BusinessModelCard({ model, onSelect }) {
  return (
    <div className="business-model-card">
      <div className="model-header">
        <h4>{model.name}</h4>
        <span className="revenue-badge">${model.revenue}/mo</span>
      </div>
      <p>{model.description}</p>
      <div className="model-metrics">
        <div className="metric">
          <span className="metric-label">Implementation</span>
          <div className="metric-bar">
            <div className="metric-fill" style={{ width: `${model.implementation * 10}%` }}></div>
          </div>
          <span className="metric-value">{model.implementation}/10</span>
        </div>
        <div className="metric">
          <span className="metric-label">Automation</span>
          <div className="metric-bar">
            <div className="metric-fill" style={{ width: `${model.automation * 10}%` }}></div>
          </div>
          <span className="metric-value">{model.automation}/10</span>
        </div>
      </div>
      <button className="btn btn-primary btn-select" onClick={() => onSelect(model.name)}>
        Select & Implement
      </button>
    </div>
  );
}


function HowItWorks() {
  const [marketSegment, setMarketSegment] = useState('');
  const [businessPreference, setBusinessPreference] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [analysisError, setAnalysisError] = useState(null); // State for API errors
  const [validationErrors, setValidationErrors] = useState({}); // { marketSegment: bool, businessPreference: bool }

  const marketSegmentRef = useRef(null);
  const businessPreferenceRef = useRef(null);

  const marketSegments = [
    { value: 'digital-products', label: 'Digital Products' },
    { value: 'e-commerce', label: 'E-commerce' },
    { value: 'saas', label: 'SaaS (Software as a Service)' },
    { value: 'online-education', label: 'Online Education' },
    { value: 'affiliate-marketing', label: 'Affiliate Marketing' },
  ];

  const businessPreferences = [
    { value: 'highest-revenue', label: 'Highest Revenue Potential' },
    { value: 'lowest-effort', label: 'Lowest Implementation Effort' },
    { value: 'fastest-implementation', label: 'Fastest Implementation Time' },
    { value: 'lowest-startup-cost', label: 'Lowest Startup Cost' },
  ];

  const handleAnalyzeClick = async () => { // Make async
    const errors = {};
    if (!marketSegment) errors.marketSegment = true;
    if (!businessPreference) errors.businessPreference = true;

    setValidationErrors(errors);

    if (Object.keys(errors).length > 0) {
      // Trigger shake animation by adding/removing class - requires CSS setup
      if (errors.marketSegment && marketSegmentRef.current) {
        marketSegmentRef.current.classList.add('shake');
        setTimeout(() => marketSegmentRef.current?.classList.remove('shake'), 600);
      }
      if (errors.businessPreference && businessPreferenceRef.current) {
        businessPreferenceRef.current.classList.add('shake');
        setTimeout(() => businessPreferenceRef.current?.classList.remove('shake'), 600);
      }
      return;
    }

    setIsLoading(true);
    setAnalysisError(null); // Clear previous errors
    setAnalysisResults([]); // Clear previous results
    setShowResults(false); // Hide results initially

    try {
      // Actual API call
      const results = await apiService.analyzeMarket(marketSegment, businessPreference);
      // Assuming the API returns an array of models directly or within a 'data' property
      const models = results?.data || results || []; // Adjust based on actual API response structure
      setAnalysisResults(models);
      setShowResults(true);
    } catch (err) {
       console.error("Error analyzing market:", err);
       const message = err?.data?.message || err?.message || 'Failed to analyze market.';
       setAnalysisError(message); // Set error state to display to user
       setShowResults(true); // Show results section to display the error
    } finally {
        setIsLoading(false);
    }
  };

  const handleBackClick = () => {
    setShowResults(false);
    setAnalysisResults([]);
    setAnalysisError(null); // Clear error when going back
    // Optionally reset form fields
    // setMarketSegment('');
    // setBusinessPreference('');
  };

  const handleSelectModel = (modelName) => {
    // TODO: Implement logic to handle model selection (e.g., navigate to implementation flow)
    alert(`You selected: ${modelName}. Starting implementation process.`);
    console.log("Selected model:", modelName);
  };


  // Add shake animation CSS (if not globally available)
  const shakeKeyframes = `
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
        }

        .shake {
            animation: shake 0.6s ease;
            border-color: var(--danger) !important; /* Ensure border changes */
        }
    `;

  return (
    <section id="how-it-works" className="how-it-works-section">
       <style>{shakeKeyframes}</style> {/* Inject CSS */}
      <div className="container">
        <div className="section-header">
          <h2>How Decision Points AI <span className="accent-text">Works</span></h2>
          <p>Streamlined process to launch and automate your business with AI</p>
        </div>
        <div className="how-it-works-steps">
          <div className="step-card">
            <span className="step-number">1</span>
            <h3>Enter Market Details</h3>
            <p>Provide information about the market segment you're targeting.</p>
          </div>
          <div className="step-card">
            <span className="step-number">2</span>
            <h3>AI Analysis</h3>
            <p>Our AI performs market analysis to identify business models.</p>
          </div>
          <div className="step-card">
            <span className="step-number">3</span>
            <h3>Select and Implement</h3>
            <p>Choose a business model and implement it with our tools.</p>
          </div>
        </div>

        {/* Market Analysis Form / Results - Moved here */}
        <div className="market-analysis-interactive">
          {!showResults ? (
            <div className="market-analysis-form">
              <h3>Analyze Your Market Potential</h3>
              <div className="form-row">
                <div className={`input-group ${validationErrors.marketSegment ? 'error' : ''}`}>
                  <label htmlFor="market-segment">Target Market Segment</label>
                  <select
                    id="market-segment"
                    className={`form-input ${validationErrors.marketSegment ? 'shake' : ''}`}
                    value={marketSegment}
                    onChange={(e) => { setMarketSegment(e.target.value); setValidationErrors(p => ({...p, marketSegment: false})); }}
                    ref={marketSegmentRef}
                  >
                    <option value="" disabled>Select a market segment...</option>
                    {marketSegments.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
                <div className={`input-group ${validationErrors.businessPreference ? 'error' : ''}`}>
                  <label htmlFor="business-preference">Business Preference</label>
                  <select
                    id="business-preference"
                    className={`form-input ${validationErrors.businessPreference ? 'shake' : ''}`}
                    value={businessPreference}
                    onChange={(e) => { setBusinessPreference(e.target.value); setValidationErrors(p => ({...p, businessPreference: false})); }}
                    ref={businessPreferenceRef}
                  >
                    <option value="" disabled>Select your preference...</option>
                    {businessPreferences.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
              </div>
              <button
                id="analyze-btn"
                className="btn btn-primary"
                onClick={handleAnalyzeClick}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <i className="fas fa-spinner fa-spin"></i> Analyzing...
                  </>
                ) : (
                  <>
                    Analyze Market <i className="fas fa-arrow-right"></i>
                  </>
                )}
              </button>
            </div>
          ) : (
            <div className="analysis-results">
              {/* Display Error Message if API call failed */}
              {analysisError && (
                <div className="error-message text-red-600 bg-red-100 border border-red-400 p-4 rounded mb-4">
                  <strong>Error:</strong> {analysisError}
                </div>
              )}

              {/* Display Results Header only if no error and results exist */}
              {!analysisError && analysisResults.length > 0 && (
                 <div className="results-header">
                   <h3>Market Analysis Results: {marketSegments.find(s => s.value === marketSegment)?.label || 'Selected Segment'}</h3>
                   <span className="badge">{analysisResults.length} Business Models Found</span>
                 </div>
              )}

              {/* Display Business Models only if no error */}
              {!analysisError && (
                <div className="business-models">
                  {analysisResults.map((model, index) => (
                    // Assuming API response matches card props (name, revenue, description, implementation, automation)
                    // Adjust mapping if API response structure is different
                    <BusinessModelCard key={model.id || index} model={model} onSelect={handleSelectModel} />
                  ))}
                </div>
              )}

              {/* Always show Back button */}
              <button className="btn btn-secondary" onClick={handleBackClick} style={{ marginTop: '1rem' }}>
                <i className="fas fa-arrow-left"></i> Back to Analysis
              </button>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

export default HowItWorks;