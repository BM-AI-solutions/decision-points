import React from 'react';

function Hero() {
  return (
    <section id="hero" className="hero-section">
      <div className="container">
        <div className="hero-content">
          <h1>Automate <span className="accent-text">Business Decisions</span> with AI</h1>
          <p>Easily launch and scale automated businesses with our advanced AI platform. Analyze markets, generate business models, and automate revenue features.</p>
          <button className="btn btn-primary btn-large">Start Free Trial <i className="fas fa-arrow-right"></i></button>
        </div>
        <div className="hero-image">
          <img src="images/hero-image.svg" alt="Decision Points AI" />
        </div>
      </div>
    </section>
  );
}

export default Hero;