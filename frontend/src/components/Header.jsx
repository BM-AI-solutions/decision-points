import React from 'react';

function Header() {
  return (
    <header className="navbar">
      <div className="container">
        <div className="logo">
          <img src="images/logo.svg" alt="Decision Points AI Logo" />
        </div>
        <ul className="nav-links">
          <li><a href="#features">Features</a></li>
          <li><a href="#how-it-works">How It Works</a></li>
          <li><a href="#pricing">Pricing</a></li>
          <li><a href="#app">Start Building</a></li>
          <li><a href="#testimonials">Testimonials</a></li>
          <li><button className="btn btn-primary">Sign Up</button></li>
        </ul>
        <button className="navbar-toggle" aria-label="Toggle Navigation">
          <i className="fas fa-bars"></i>
        </button>
      </div>
    </header>
  );
}

export default Header;