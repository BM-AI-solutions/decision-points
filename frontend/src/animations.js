/**
 * Animations for Decision Points UI
 * Implements Intersection Observer API for triggering animations when elements enter viewport
 */

// Throttling function
const throttle = (func, limit) => {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Observer options
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  // Create observer
  // Commenting out Intersection Observer for performance testing
  /*
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);
  */

  // Observe all elements with animate-on-scroll class
  // Commenting out Intersection Observer for performance testing
  /*
  document.querySelectorAll('.animate-on-scroll').forEach(el => {
    observer.observe(el);
  });
  */
  
  // Navigation enhancement - highlight active section on scroll
  const sections = document.querySelectorAll('section, .hero, .features, .how-it-works, .dashboard-preview, .pricing, .app-section, .testimonials');
  const navLinks = document.querySelectorAll('.nav-link');
  
  // Function to set active nav link
  const setActiveNavLink = () => {
    let currentSection = '';
    
    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.clientHeight;
      
      if (window.scrollY >= (sectionTop - 200)) {
        currentSection = section.getAttribute('id') || '';
      }
    });
    
    navLinks.forEach(link => {
      link.classList.remove('active');
      const href = link.getAttribute('href');
      
      if (href && href.substring(1) === currentSection) {
        link.classList.add('active');
      }
    });
  };
  
  // Initial call to set active nav link
  setActiveNavLink();
  
  // Add scroll event listener for active nav highlighting
  // Throttled to improve performance
  window.addEventListener('scroll', throttle(setActiveNavLink, 100)); // Throttle to 100ms

  // Navbar appearance change on scroll
  const navbar = document.querySelector('.navbar');

  const updateNavbarAppearance = () => {
    // Only run if navbar exists
    if (navbar) {
      if (window.scrollY > 50) {
        navbar.classList.add('navbar-scrolled');
      } else {
        navbar.classList.remove('navbar-scrolled');
      }
    }
  };

  // Initial call to set navbar appearance (only if navbar exists)
  if (navbar) {
    updateNavbarAppearance();
    // Add scroll event listener for navbar appearance (only if navbar exists)
    // Throttled to improve performance
    window.addEventListener('scroll', throttle(updateNavbarAppearance, 100)); // Throttle to 100ms
  }

  // Mobile menu toggle enhancement
  const mobileMenuToggle = document.querySelector('.navbar-toggle');
  const navMenu = document.querySelector('.nav-menu');
  
  if (mobileMenuToggle && navMenu) {
    // Close mobile menu when clicking on a nav link
    navMenu.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        if (navMenu.classList.contains('active')) {
          navMenu.classList.remove('active');
          document.body.classList.remove('menu-open');
        }
      });
    });
    
    // Toggle body class for preventing scroll when menu is open
    mobileMenuToggle.addEventListener('click', () => {
      if (navMenu.classList.contains('active')) {
        document.body.classList.remove('menu-open');
      } else {
        document.body.classList.add('menu-open');
      }
    });
  }

  // Add flame flicker effect to specific elements
  document.querySelectorAll('.flame-effect').forEach(el => {
    el.style.animation = `flame-flicker ${2 + Math.random()}s infinite alternate ease-in-out`;
  });

  // Add ember glow effect to specific elements
  document.querySelectorAll('.ember-glow').forEach(el => {
    el.style.animation = `ember-glow ${3 + Math.random()}s infinite alternate ease-in-out`;
  });

  // Add parallax effect to hero section
  const heroSection = document.querySelector('.hero');
  if (heroSection) {
    // Throttled scroll listener for parallax effect
    window.addEventListener('scroll', throttle(() => {
      const scrollPosition = window.scrollY;
      if (scrollPosition < 800) { // Only apply effect near the top of the page
        const parallaxElements = heroSection.querySelectorAll('.parallax');
        parallaxElements.forEach(el => {
          const speed = el.getAttribute('data-speed') || 0.2;
          el.style.transform = `translateY(${scrollPosition * speed}px)`;
        });
      }
    }, 100)); // Throttle to 100ms
  }

  // Add hover effect for cards (refactored to CSS)
  // Removed JavaScript logic for dynamic glow element creation/removal
});
