import React from 'react';

function Testimonials() {
  return (
    <section id="testimonials" className="testimonials-section">
      <div className="container">
        <div className="section-header">
          <h2>What Our <span className="accent-text">Clients Say</span></h2>
          <p>Success stories from entrepreneurs using Decision Points AI</p>
        </div>
        <div className="testimonial-slider">
          <div className="testimonial-card">
            <div className="testimonial-content">
              <p>"Decision Points AI transformed my business approach. The market analysis was spot-on, and the automated features saved me countless hours."</p>
            </div>
            <div className="testimonial-author">
              <img src="images/testimonial-1.jpg" alt="Testimonial Author" />
              <div className="author-info">
                <h4>Sarah Johnson</h4>
                <p>E-Commerce Entrepreneur</p>
              </div>
            </div>
          </div>
          <div className="testimonial-controls">
            <button className="testimonial-control prev" aria-label="Previous testimonial">
              <i className="fas fa-chevron-left"></i>
            </button>
            <div className="testimonial-dots">
              <span className="dot active"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
            <button className="testimonial-control next" aria-label="Next testimonial">
              <i className="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Testimonials;