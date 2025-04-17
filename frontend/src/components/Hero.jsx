import React from 'react';

function Hero() {
  return (
    <section id="hero" className="hero">
      <div className="container">
        <div className="hero-content animate-on-scroll">
          <h1>Automate <span className="accent-text">Business Decisions</span> with AI</h1>
          <p>Easily launch and scale automated businesses with our advanced AI platform. Analyze markets, generate business models, and automate revenue features.</p>
          <button className="btn btn-primary btn-large ember-glow">Start Free Trial <i className="fas fa-arrow-right"></i></button>
        </div>
        <div className="hero-image animate-on-scroll">
          <img src="images/hero-image.svg" alt="Decision Points AI" className="parallax" data-speed="0.05" />
        </div>
      </div>
      <div className="hero-gradient parallax" data-speed="0.1"></div>
    </section>
  );
}

export default Hero;