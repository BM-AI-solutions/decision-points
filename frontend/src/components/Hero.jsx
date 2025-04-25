import React from 'react';
import styles from './Hero.module.css'; // Assuming you have a CSS module for Hero

function Hero() {
  return (
    <section id="hero" className={styles.heroSection}>
      <div className="container">
        <div className={styles.heroContent}>
          <h1>Automate <span className="accent-text">Business Decisions</span> with AI</h1>
          <p>Easily launch and scale automated businesses with our advanced AI platform. Analyze markets, generate business models, and automate revenue features.</p>
          <button className="btn btn-primary btn-large">Start Free Trial <i className="fas fa-arrow-right"></i></button>
        </div>
        <div className={styles.heroImage}>
          <img src="images/hero-image.svg" alt="Decision Points AI" />
        </div>
      </div>
    </section>
  );
}

export default Hero;