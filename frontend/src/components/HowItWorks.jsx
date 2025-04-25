import React from 'react';

function HowItWorks() {
  return (
    <section id="how-it-works" className="how-it-works-section">
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
      </div>
    </section>
  );
}

export default HowItWorks;