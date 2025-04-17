import React, { useState, useEffect, useRef } from 'react';

const testimonialsData = [
  {
    id: 1,
    quote: "Decision Points AI transformed my business approach. The market analysis was spot-on, and the automated features saved me countless hours.",
    author: "Sarah Johnson",
    title: "E-Commerce Entrepreneur",
    image: "images/testimonial-1.jpg"
  },
  {
    id: 2, // Assuming there's a second testimonial image/data
    quote: "The insights provided by the platform were invaluable for pivoting my SaaS product. Highly recommended for data-driven decisions.",
    author: "Michael Chen",
    title: "SaaS Founder",
    image: "images/testimonial-2.jpg" // Make sure this image exists
  },
  {
    id: 3, // Assuming there's a third testimonial image/data
    quote: "As a consultant, I use Decision Points AI to quickly validate business ideas for my clients. It's an essential tool in my arsenal.",
    author: "Jessica Williams",
    title: "Business Consultant",
    image: "images/testimonial-3.jpg" // Make sure this image exists
  }
];


function Testimonials() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const timeoutRef = useRef(null);
  const sliderRef = useRef(null); // Ref for the slider container

  const resetTimeout = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
  };

  useEffect(() => {
    resetTimeout();
    timeoutRef.current = setTimeout(
      () =>
        setCurrentSlide((prevIndex) =>
          prevIndex === testimonialsData.length - 1 ? 0 : prevIndex + 1
        ),
      5000 // Change slide every 5 seconds
    );

    return () => {
      resetTimeout();
    };
  }, [currentSlide]);

  // Pause on hover
   useEffect(() => {
    const sliderElement = sliderRef.current;
    if (!sliderElement) return;

    const handleMouseEnter = () => {
      resetTimeout(); // Clear the auto-slide timer
    };

    const handleMouseLeave = () => {
      // Restart the timer when mouse leaves
      resetTimeout();
      timeoutRef.current = setTimeout(
        () =>
          setCurrentSlide((prevIndex) =>
            prevIndex === testimonialsData.length - 1 ? 0 : prevIndex + 1
          ),
        5000
      );
    };

    sliderElement.addEventListener('mouseenter', handleMouseEnter);
    sliderElement.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      // Cleanup listeners when component unmounts
      sliderElement.removeEventListener('mouseenter', handleMouseEnter);
      sliderElement.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []); // Empty dependency array ensures this runs only once on mount/unmount


  const nextSlide = () => {
    setCurrentSlide((prevIndex) =>
      prevIndex === testimonialsData.length - 1 ? 0 : prevIndex + 1
    );
  };

  const prevSlide = () => {
    setCurrentSlide((prevIndex) =>
      prevIndex === 0 ? testimonialsData.length - 1 : prevIndex - 1
    );
  };

  const goToSlide = (index) => {
    setCurrentSlide(index);
  };


  return (
    <section id="testimonials" className="testimonials-section">
      <div className="container">
        <div className="section-header">
          <h2>What Our <span className="accent-text">Clients Say</span></h2>
          <p>Success stories from entrepreneurs using Decision Points AI</p>
        </div>
        {/* Add ref to the slider container */}
        <div className="testimonial-slider" ref={sliderRef}>
          {/* Map through testimonials, only render the active one */}
          {testimonialsData.map((testimonial, index) => (
            <div
              key={testimonial.id}
              className={`testimonial-card ${index === currentSlide ? 'active' : ''}`}
              style={{ display: index === currentSlide ? 'block' : 'none' }} // Simple show/hide
            >
              <div className="testimonial-content">
                <p>"{testimonial.quote}"</p>
              </div>
              <div className="testimonial-author">
                <img src={testimonial.image} alt={testimonial.author} />
                <div className="author-info">
                  <h4>{testimonial.author}</h4>
                  <p>{testimonial.title}</p>
                </div>
              </div>
            </div>
          ))}
          <div className="testimonial-controls">
             {/* Add onClick handler */}
            <button className="testimonial-control prev" aria-label="Previous testimonial" onClick={prevSlide}>
              <i className="fas fa-chevron-left"></i>
            </button>
            <div className="testimonial-dots">
               {/* Map through data to create dots */}
              {testimonialsData.map((_, index) => (
                <span
                  key={index}
                  className={`dot ${index === currentSlide ? 'active' : ''}`}
                  onClick={() => goToSlide(index)} // Add onClick handler
                ></span>
              ))}
            </div>
             {/* Add onClick handler */}
            <button className="testimonial-control next" aria-label="Next testimonial" onClick={nextSlide}>
              <i className="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Testimonials;