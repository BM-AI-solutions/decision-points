/**
 * API utility for the Dual Agent System
 * 
 * This file contains functions for making API requests to the backend
 * through Cloudflare Workers proxy.
 */

// API client with consistent configuration
class ApiClient {
  constructor() {
    // Get configuration from the global CONFIG object
    this.baseUrl = window.APP_CONFIG?.API?.BASE_URL || '/api';
    this.timeout = window.APP_CONFIG?.API?.TIMEOUT || 60000;
    this.withCredentials = window.APP_CONFIG?.API?.WITH_CREDENTIALS || true;
  }

  /**
   * Make a request to the API
   * 
   * @param {string} endpoint - API endpoint path (without the base URL)
   * @param {Object} options - Request options
   * @param {string} options.method - HTTP method (GET, POST, PUT, DELETE)
   * @param {Object} options.data - Request payload for POST/PUT requests
   * @param {Object} options.params - URL parameters for GET requests
   * @param {Object} options.headers - Additional headers
   * @returns {Promise<any>} API response
   */
  async request(endpoint, options = {}) {
    const {
      method = 'GET',
      data = null,
      params = {},
      headers = {},
    } = options;

    // Build the URL with query parameters
    let url = `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;
    
    // Add query parameters
    if (Object.keys(params).length > 0) {
      const queryParams = new URLSearchParams();
      for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value);
        }
      }
      url += `?${queryParams.toString()}`;
    }

    // Set up request options
    const requestOptions = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...headers,
      },
      credentials: this.withCredentials ? 'include' : 'same-origin',
    };

    // Add body for POST/PUT requests
    if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
      requestOptions.body = JSON.stringify(data);
    }

    try {
      // Set up timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);
      requestOptions.signal = controller.signal;

      // Make the request
      const response = await fetch(url, requestOptions);
      clearTimeout(timeoutId);

      // Handle HTTP errors
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw {
          status: response.status,
          statusText: response.statusText,
          data: errorData,
        };
      }

      // Parse JSON response
      const responseData = await response.json();
      return responseData;
    } catch (error) {
      // Handle timeout errors
      if (error.name === 'AbortError') {
        throw {
          status: 408,
          statusText: 'Request Timeout',
          data: { message: 'The request timed out' },
        };
      }
      
      // Re-throw other errors
      throw error;
    }
  }

  // HTTP method wrappers
  async get(endpoint, params = {}, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET', params });
  }

  async post(endpoint, data = {}, options = {}) {
    return this.request(endpoint, { ...options, method: 'POST', data });
  }

  async put(endpoint, data = {}, options = {}) {
    return this.request(endpoint, { ...options, method: 'PUT', data });
  }

  async delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }
}

// Create a singleton instance
const api = new ApiClient();

// Export specific API functions for the application
const apiService = {
  // Market analysis
  analyzeMarket: (marketSegment, businessPreference) => {
    return api.post('/market/analyze', {
      market_segment: marketSegment,
      business_preference: businessPreference
    });
  },
  
  // Business models
  getBusinessModels: () => {
    return api.get('/business/models');
  },
  
  getBusinessModel: (modelId) => {
    return api.get(`/business/models/${modelId}`);
  },
  
  createBusinessModel: (modelData) => {
    return api.post('/business/models', modelData);
  },
  
  // Features
  getFeatures: (businessModelId) => {
    return api.get('/features', { business_model_id: businessModelId });
  },
  
  implementFeature: (featureId, options) => {
    return api.post(`/features/${featureId}/implement`, options);
  },
  
  // User authentication
  login: (email, password) => {
    return api.post('/auth/login', { email, password });
  },
  
  signup: (userData) => {
    return api.post('/auth/signup', userData);
  },
  
  logout: () => {
    return api.post('/auth/logout');
  },
  
  getCurrentUser: () => {
    return api.get('/auth/user');
  },
  
  // System health and configuration
  getHealthStatus: () => {
    return api.get('/health');
  },
  
  getConfig: () => {
    return api.get('/config');
  }
};

// Make the API service available globally
window.apiService = apiService;
