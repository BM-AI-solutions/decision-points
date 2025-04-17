/**
 * API utility for the Dual Agent System
 *
 * This file contains functions for making API requests to the backend.
 */

// API client with consistent configuration
class ApiClient {
  constructor() {
    // Get configuration from Vite environment variables
    // Ensure these are defined in your .env file (e.g., VITE_API_BASE_URL=/api)
    this.baseUrl = import.meta.env.VITE_API_BASE_URL || '/api';
    this.timeout = parseInt(import.meta.env.VITE_API_TIMEOUT || '60000', 10); // Default 60 seconds
    // Convert string 'true'/'false' to boolean, default true
    this.withCredentials = (import.meta.env.VITE_API_WITH_CREDENTIALS !== 'false');
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
      const queryString = queryParams.toString();
      if (queryString) {
          url += `?${queryString}`;
      }
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

    // Add body for POST/PUT/PATCH requests
    if (data && ['POST', 'PUT', 'PATCH'].includes(method.toUpperCase())) {
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
        let errorData = {};
        try {
            // Try to parse error response as JSON
            errorData = await response.json();
        } catch (e) {
            // If not JSON, maybe plain text?
            try {
                errorData = { message: await response.text() };
            } catch (textError) {
                // If reading text fails, use a generic message
                errorData = { message: 'Failed to parse error response.' };
            }
        }
        console.error(`API Error ${response.status}:`, errorData); // Log the error details
        throw {
          status: response.status,
          statusText: response.statusText,
          data: errorData, // Include parsed error data if available
        };
      }

      // Handle empty response body for certain statuses (e.g., 204 No Content)
      if (response.status === 204) {
        return null; // Or return an empty object/success indicator as needed
      }

      // Parse JSON response for other successful requests
      const responseData = await response.json();
      return responseData;
    } catch (error) {
      // Handle timeout errors specifically
      if (error.name === 'AbortError') {
         console.error('API Request Timeout:', url);
        throw {
          status: 408,
          statusText: 'Request Timeout',
          data: { message: `The request to ${url} timed out after ${this.timeout}ms` },
        };
      }

      // Log and re-throw other errors (including network errors or previously thrown HTTP errors)
      console.error('API Request Failed:', error);
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
const apiClientInstance = new ApiClient();

// Export specific API functions for the application
const apiService = {
  // Market analysis
  analyzeMarket: (marketSegment, businessPreference) => {
    console.log("API Call: analyzeMarket", { marketSegment, businessPreference }); // Added logging
    return apiClientInstance.post('/market/analyze', {
      market_segment: marketSegment,
      business_preference: businessPreference
    });
  },

  // Business models
  getBusinessModels: () => {
    console.log("API Call: getBusinessModels"); // Added logging
    return apiClientInstance.get('/business/models');
  },

  getBusinessModel: (modelId) => {
    console.log("API Call: getBusinessModel", { modelId }); // Added logging
    return apiClientInstance.get(`/business/models/${modelId}`);
  },

  createBusinessModel: (modelData) => {
    console.log("API Call: createBusinessModel", modelData); // Added logging
    return apiClientInstance.post('/business/models', modelData);
  },

  // Features
  getFeatures: (businessModelId) => {
    console.log("API Call: getFeatures", { businessModelId }); // Added logging
    return apiClientInstance.get('/features', { business_model_id: businessModelId });
  },

  implementFeature: (featureId, options) => {
    console.log("API Call: implementFeature", { featureId, options }); // Added logging
    return apiClientInstance.post(`/features/${featureId}/implement`, options);
  },

  // User authentication
  login: (email, password) => {
    console.log("API Call: login"); // Added logging (don't log password)
    return apiClientInstance.post('/auth/login', { email, password });
  },

  signup: (userData) => {
    console.log("API Call: signup", userData); // Added logging
    return apiClientInstance.post('/auth/register', userData); // Corrected path from /signup
  },

  logout: () => {
    console.log("API Call: logout"); // Added logging
    return apiClientInstance.post('/auth/logout');
  },

  getCurrentUser: () => {
    console.log("API Call: getCurrentUser"); // Added logging
    return apiClientInstance.get('/auth/user');
  },

  // OAuth authentication
  loginWithGoogle: (data) => {
    console.log("API Call: loginWithGoogle"); // Added logging
    return apiClientInstance.post('/auth/google', data);
  },

  loginWithGithub: (data) => {
    console.log("API Call: loginWithGithub"); // Added logging
    return apiClientInstance.post('/auth/github', data);
  },

  // Subscription management
  getSubscriptionPlans: () => {
    console.log("API Call: getSubscriptionPlans"); // Added logging
    return apiClientInstance.get('/subscriptions/plans');
  },

  getCurrentSubscription: () => {
    console.log("API Call: getCurrentSubscription"); // Added logging
    return apiClientInstance.get('/subscriptions/current');
  },

  createCheckoutSession: (data) => {
    console.log("API Call: createCheckoutSession", data); // Added logging
    return apiClientInstance.post('/subscriptions/create-checkout-session', data);
  },

  updateSubscription: (subscriptionId, data) => {
    console.log("API Call: updateSubscription", { subscriptionId, data }); // Added logging
    return apiClientInstance.put(`/subscriptions/${subscriptionId}`, data);
  },

  cancelSubscription: (subscriptionId) => {
    console.log("API Call: cancelSubscription", { subscriptionId }); // Added logging
    return apiClientInstance.post(`/subscriptions/${subscriptionId}/cancel`);
  },

  reactivateSubscription: (subscriptionId) => {
    console.log("API Call: reactivateSubscription", { subscriptionId }); // Added logging
    return apiClientInstance.post(`/subscriptions/${subscriptionId}/reactivate`);
  },

  // System health and configuration
  getHealthStatus: () => {
    console.log("API Call: getHealthStatus"); // Added logging
    return apiClientInstance.get('/health');
  },

  getConfig: () => {
    console.log("API Call: getConfig"); // Added logging
    return apiClientInstance.get('/config');
  }
};

// Export the service object for use in components
export default apiService;