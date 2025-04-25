/**
 * Ember Effects - Adds dynamic fiery particle effects to the website
 * Part of the "Apple from Hell" UI/UX theme
 */

// Create ember particles for a specific element
function createEmberParticles(parentElement, count = 20) {
  // Create container for particles
  const particlesContainer = document.createElement('div');
  particlesContainer.className = 'ember-particles';
  parentElement.appendChild(particlesContainer);
  
  // Create individual particles
  for (let i = 0; i < count; i++) {
    const particle = document.createElement('div');
    particle.className = 'ember-particle';
    
    // Randomize particle properties
    const size = Math.random() * 4 + 2; // 2-6px
    const xOffset = Math.random() * 2 - 1; // -1 to 1
    const delay = Math.random() * 8; // 0-8s delay
    const duration = Math.random() * 4 + 6; // 6-10s duration
    
    // Apply styles
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;
    particle.style.left = `${Math.random() * 100}%`;
    particle.style.bottom = '0';
    particle.style.opacity = '0';
    particle.style.setProperty('--x-offset', xOffset);
    particle.style.animation = `ember-rise ${duration}s infinite linear`;
    particle.style.animationDelay = `${delay}s`;
    
    // Add to container
    particlesContainer.appendChild(particle);
  }
}

// Add ember glow effect to elements
function addEmberGlowToElements() {
  // Add to primary buttons
  document.querySelectorAll('.btn-primary').forEach(btn => {
    btn.classList.add('ember-glow');
  });
  
  // Add to feature cards
  document.querySelectorAll('.feature-card').forEach((card, index) => {
    // Stagger the animation
    setTimeout(() => {
      card.classList.add('ember-glow');
    }, index * 200);
  });
}

// Add infernal glow to specific elements
function addInfernalGlowToElements() {
  // Add to hero section elements
  const heroTitle = document.querySelector('.hero-content h1 .accent-text');
  if (heroTitle) {
    heroTitle.classList.add('infernal-glow');
    heroTitle.classList.add('text-glow');
  }
  
  // Add to pricing cards
  document.querySelectorAll('.pricing-card.featured').forEach(card => {
    card.classList.add('infernal-glow');
    card.classList.add('hellfire-border');
  });
}

// Add floating animation to elements
function addFloatingAnimation() {
  // Hero image
  const heroImage = document.querySelector('.hero-image img');
  if (heroImage) {
    heroImage.classList.add('float');
  }
  
  // Dashboard preview
  const dashboardPreview = document.querySelector('.dashboard-mockup');
  if (dashboardPreview) {
    dashboardPreview.classList.add('float');
  }
}

// Add staggered fade-in animations
function addStaggeredAnimations() {
  // Feature cards container
  const featureCards = document.querySelector('.grid-cols-1.gap-8');
  if (featureCards) {
    featureCards.classList.add('stagger-fade-in');
  }
  
  // How it works steps
  const howItWorksSteps = document.querySelector('.grid-cols-1.gap-8.md\\:grid-cols-3');
  if (howItWorksSteps) {
    howItWorksSteps.classList.add('stagger-fade-in');
  }
}

// Initialize all effects
function initializeEmberEffects() {
  // Wait for DOM to be fully loaded
  document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Ember Effects');
    
    // Add ember particles to hero section
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
      createEmberParticles(heroSection, 30);
    }
    
    // Add ember particles to footer
    const footer = document.querySelector('footer');
    if (footer) {
      createEmberParticles(footer, 15);
    }
    
    // Add glow effects
    addEmberGlowToElements();
    addInfernalGlowToElements();
    
    // Add floating animations
    addFloatingAnimation();
    
    // Add staggered animations
    addStaggeredAnimations();
    
    // Add hover effects to buttons
    document.querySelectorAll('.btn').forEach(btn => {
      btn.classList.add('btn-hover-effect');
    });
  });
}

// Export the initialization function
export default initializeEmberEffects;
