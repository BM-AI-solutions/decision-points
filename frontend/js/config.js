/**
 * Configuration file for the Dual Agent System frontend
 * 
 * This file contains environment-specific settings for the application.
 * Update these values before deployment.
 */

const CONFIG = {
  // API Settings
  API: {
    // Base URL for API requests
    // In production with Cloudflare, this should be just '/api'
    // The Cloudflare Worker will handle routing to the actual GCP Function
    BASE_URL: '/api',
    
    // Default timeout for API requests in milliseconds
    TIMEOUT: 60000,
    
    // Whether to include credentials with API requests
    WITH_CREDENTIALS: true
  },
  
  // Feature Flags
  FEATURES: {
    // Enable/disable features as needed
    ENABLE_LOGS: false,
    ENABLE_ANALYTICS: false,
    DARK_MODE_DEFAULT: true
  },
  
  // Application Settings
  APP: {
    NAME: 'Dual Agent System',
    VERSION: '1.0.0',
    CONTACT_EMAIL: 'support@intellisol.cc'
  }
};

// Make the config available globally
window.APP_CONFIG = CONFIG;
