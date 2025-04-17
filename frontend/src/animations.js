/**
 * Animations for Decision Points UI
 * Implements Intersection Observer API for triggering animations when elements enter viewport
 */

document.addEventListener('DOMContentLoaded', () => {
  // Observer options
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  // Create observer
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Observe all elements with animate-on-scroll class
  document.querySelectorAll('.animate-on-scroll').forEach(el => {
    observer.observe(el);
  });
  
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
  window.addEventListener('scroll', setActiveNavLink);
  
  // Navbar appearance change on scroll
  const navbar = document.querySelector('.navbar');
  
  const updateNavbarAppearance = () => {
    if (window.scrollY > 50) {
      navbar.classList.add('navbar-scrolled');
    } else {
      navbar.classList.remove('navbar-scrolled');
    }
  };
  
  // Initial call to set navbar appearance
  updateNavbarAppearance();
  
  // Add scroll event listener for navbar appearance
  window.addEventListener('scroll', updateNavbarAppearance);
  
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
    window.addEventListener('scroll', () => {
      const scrollPosition = window.scrollY;
      if (scrollPosition < 800) { // Only apply effect near the top of the page
        const parallaxElements = heroSection.querySelectorAll('.parallax');
        parallaxElements.forEach(el => {
          const speed = el.getAttribute('data-speed') || 0.2;
          el.style.transform = `translateY(${scrollPosition * speed}px)`;
        });
      }
    });
  }

  // Add hover effect for cards
  document.querySelectorAll('.feature-card, .pricing-card, .testimonial-card').forEach(card => {
    card.addEventListener('mouseenter', (e) => {
      const glowElement = document.createElement('div');
      glowElement.classList.add('card-glow');
      glowElement.style.position = 'absolute';
      glowElement.style.top = '0';
      glowElement.style.left = '0';
      glowElement.style.right = '0';
      glowElement.style.bottom = '0';
      glowElement.style.borderRadius = 'inherit';
      glowElement.style.pointerEvents = 'none';
      glowElement.style.animation = 'card-glow 2s infinite alternate ease-in-out';
      glowElement.style.zIndex = '0';
      
      // Only add if it doesn't already have one
      if (!card.querySelector('.card-glow')) {
        card.style.position = 'relative';
        card.appendChild(glowElement);
      }
    });
    
    card.addEventListener('mouseleave', (e) => {
      const glowElement = card.querySelector('.card-glow');
      if (glowElement) {
        glowElement.remove();
      }
    });
  });
});