/**
 * Stripe payment integration for the Dual Agent System
 * 
 * Handles subscription management and payment processing
 * through the Stripe API.
 */

class StripeService {
  constructor() {
    this.publishableKey = 'pk_live_51QQkmTGpp9i49TTk5Bcw19pGK3Y8iR8O1Th4Y245vP5GecdHoZfFC6YqPFDTtSyxeK7buc8EqB39RR7Py9ptTcei00Vq7FcmlC';
    this.stripe = null;
    
    // Load Stripe.js
    this.loadStripeScript();
    
    // Set up event listeners for pricing buttons
    this.setupEventListeners();
  }
  
  /**
   * Load the Stripe.js script
   */
  loadStripeScript() {
    // Only load if not already loaded
    if (window.Stripe) {
      this.initializeStripe();
      return;
    }
    
    const script = document.createElement('script');
    script.src = 'https://js.stripe.com/v3/';
    script.async = true;
    document.head.appendChild(script);
    
    script.onload = () => {
      this.initializeStripe();
    };
  }
  
  /**
   * Initialize Stripe with API key
   */
  initializeStripe() {
    if (window.Stripe) {
      this.stripe = Stripe(this.publishableKey);
      console.log('Stripe initialized');
    } else {
      console.error('Stripe.js failed to load');
    }
  }
  
  /**
   * Set up event listeners for subscription buttons
   */
  setupEventListeners() {
    // Find all pricing buttons
    const pricingButtons = document.querySelectorAll('.pricing-card .btn');
    
    pricingButtons.forEach(button => {
      button.addEventListener('click', (event) => {
        event.preventDefault();
        
        // Only proceed if user is logged in
        if (!window.authService?.currentUser) {
          authService.showNotification('Please sign in to subscribe', 'info');
          authService.openLoginModal();
          return;
        }
        
        // Get plan details from the pricing card
        const pricingCard = button.closest('.pricing-card');
        if (!pricingCard) return;
        
        const planName = pricingCard.querySelector('h3')?.textContent || 'Unknown Plan';
        const priceElement = pricingCard.querySelector('.amount');
        const price = priceElement ? parseInt(priceElement.textContent) : 0;
        const isYearly = pricingCard.querySelector('.period')?.textContent === '/yr';
        
        // Get plan ID based on plan name and billing cycle
        const planId = this.getPlanId(planName, isYearly);
        
        // Proceed with subscription
        if (planId) {
          this.subscribeUser(planId, planName, isYearly);
        } else {
          // Handle enterprise plan differently
          if (planName.includes('Enterprise')) {
            this.showEnterpriseContactForm();
          } else {
            authService.showNotification('Unable to process subscription request', 'error');
          }
        }
      });
    });
  }
  
  /**
   * Get Stripe plan ID based on plan name and billing cycle
   */
  getPlanId(planName, isYearly) {
    // Map plan names to their IDs
    // These would be replaced with actual Stripe plan IDs
    const planIds = {
      'Starter': {
        monthly: 'price_starter_monthly',
        yearly: 'price_starter_yearly'
      },
      'Professional': {
        monthly: 'price_professional_monthly',
        yearly: 'price_professional_yearly'
      },
      'Enterprise': {
        monthly: 'price_enterprise_monthly',
        yearly: 'price_enterprise_yearly'
      }
    };
    
    // Normalize plan name to match keys
    const normalizedName = Object.keys(planIds).find(key => 
      planName.includes(key)
    );
    
    if (!normalizedName) return null;
    
    return planIds[normalizedName][isYearly ? 'yearly' : 'monthly'];
  }
  
  /**
   * Initiate the subscription process for a user
   */
  async subscribeUser(planId, planName, isYearly) {
    try {
      // Show loading state
      authService.showNotification('Processing subscription request...', 'info');
      
      // Request checkout session from backend
      const response = await apiService.createCheckoutSession({
        plan_id: planId,
        success_url: window.location.origin + '/subscription/success',
        cancel_url: window.location.origin + '/subscription/cancel'
      });
      
      // Redirect to Stripe checkout
      if (response && response.sessionId) {
        await this.stripe.redirectToCheckout({
          sessionId: response.sessionId
        });
      } else {
        throw new Error('Invalid session response');
      }
    } catch (error) {
      console.error('Subscription error:', error);
      authService.showNotification('Subscription failed: ' + (error.message || 'Please try again'), 'error');
    }
  }
  
  /**
   * Show the enterprise contact form
   */
  showEnterpriseContactForm() {
    const appModal = document.getElementById('app-modal');
    if (!appModal) return;
    
    // Set content for enterprise contact form
    const modalBody = appModal.querySelector('.modal-body');
    if (modalBody) {
      modalBody.innerHTML = `
        <form class="contact-form">
          <h3>Enterprise Plan Request</h3>
          <p>Please fill out the form below and our sales team will contact you shortly.</p>
          
          <div class="input-group">
            <label for="company-name">Company Name</label>
            <input type="text" id="company-name" class="form-input" placeholder="Your company">
          </div>
          
          <div class="input-group">
            <label for="company-size">Company Size</label>
            <select id="company-size" class="form-input">
              <option value="">Select company size</option>
              <option value="1-10">1-10 employees</option>
              <option value="11-50">11-50 employees</option>
              <option value="51-200">51-200 employees</option>
              <option value="201-500">201-500 employees</option>
              <option value="501+">501+ employees</option>
            </select>
          </div>
          
          <div class="input-group">
            <label for="contact-name">Contact Name</label>
            <input type="text" id="contact-name" class="form-input" placeholder="Your name">
          </div>
          
          <div class="input-group">
            <label for="contact-email">Contact Email</label>
            <input type="email" id="contact-email" class="form-input" placeholder="your@email.com">
          </div>
          
          <div class="input-group">
            <label for="contact-phone">Contact Phone</label>
            <input type="tel" id="contact-phone" class="form-input" placeholder="Your phone">
          </div>
          
          <div class="input-group">
            <label for="requirements">Specific Requirements</label>
            <textarea id="requirements" class="form-input" rows="4" placeholder="Tell us about your specific requirements..."></textarea>
          </div>
          
          <button type="submit" class="btn btn-primary btn-full">Submit Request</button>
        </form>
      `;
      
      // Set header title
      const modalHeader = appModal.querySelector('.modal-header h3');
      if (modalHeader) {
        modalHeader.textContent = 'Contact Enterprise Sales';
      }
      
      // Add event listener to the form
      const form = modalBody.querySelector('form');
      if (form) {
        form.addEventListener('submit', async (e) => {
          e.preventDefault();
          
          const companyName = document.getElementById('company-name').value;
          const companySize = document.getElementById('company-size').value;
          const contactName = document.getElementById('contact-name').value;
          const contactEmail = document.getElementById('contact-email').value;
          const contactPhone = document.getElementById('contact-phone').value;
          const requirements = document.getElementById('requirements').value;
          
          // Validate form
          if (!companyName || !companySize || !contactName || !contactEmail) {
            authService.showNotification('Please fill out all required fields', 'error');
            return;
          }
          
          try {
            // Send request to backend
            await apiService.submitEnterpriseSalesRequest({
              company_name: companyName,
              company_size: companySize,
              contact_name: contactName,
              contact_email: contactEmail,
              contact_phone: contactPhone,
              requirements
            });
            
            // Show success message
            modalBody.innerHTML = `
              <div class="success-message">
                <i class="fas fa-check-circle" style="font-size: 3rem; color: var(--success); margin-bottom: 1rem;"></i>
                <h3>Request Submitted!</h3>
                <p>Thank you for your interest in our Enterprise plan. Our sales team will contact you within 24 hours.</p>
                <button class="btn btn-primary btn-full" id="close-modal">Done</button>
              </div>
            `;
            
            // Add event listener to close button
            document.getElementById('close-modal')?.addEventListener('click', () => {
              authService.closeAllModals();
            });
          } catch (error) {
            authService.showNotification('Failed to submit request: ' + (error.message || 'Please try again'), 'error');
          }
        });
      }
    }
    
    // Display the modal
    appModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  }
  
  /**
   * Update user subscription
   */
  async updateSubscription(subscriptionId, planId) {
    try {
      return await apiService.updateSubscription(subscriptionId, {
        plan_id: planId
      });
    } catch (error) {
      console.error('Subscription update error:', error);
      throw error;
    }
  }
  
  /**
   * Cancel user subscription
   */
  async cancelSubscription(subscriptionId) {
    try {
      return await apiService.cancelSubscription(subscriptionId);
    } catch (error) {
      console.error('Subscription cancellation error:', error);
      throw error;
    }
  }
  
  /**
   * Get user's current subscription
   */
  async getCurrentSubscription() {
    try {
      return await apiService.getCurrentSubscription();
    } catch (error) {
      console.error('Get subscription error:', error);
      return null;
    }
  }
}

// Initialize Stripe service
const stripeService = new StripeService();

// Add API methods for Stripe integration
Object.assign(apiService, {
  createCheckoutSession: (data) => {
    return api.post('/subscriptions/create-checkout-session', data);
  },
  
  getCurrentSubscription: () => {
    return api.get('/subscriptions/current');
  },
  
  updateSubscription: (subscriptionId, data) => {
    return api.put(`/subscriptions/${subscriptionId}`, data);
  },
  
  cancelSubscription: (subscriptionId) => {
    return api.post(`/subscriptions/${subscriptionId}/cancel`);
  },
  
  submitEnterpriseSalesRequest: (data) => {
    return api.post('/contact/enterprise', data);
  }
});

// Export Stripe service
window.stripeService = stripeService;
