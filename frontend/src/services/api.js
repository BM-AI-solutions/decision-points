/**
 * API utility for the Dual Agent System
 *
 * This file contains functions for making API requests to the backend.
 */

// Define API base URL for export
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// API client with consistent configuration
class ApiClient {
  constructor() {
    // Get configuration from Vite environment variables
    // Since all endpoints now include the '/api/' prefix, we set the base URL to an empty string
    this.baseUrl = API_BASE_URL;
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

    // Get auth token from localStorage
    const authToken = localStorage.getItem('authToken');

    // Set up request options
    const requestOptions = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        // Add Authorization header if token exists
        ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {}),
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
      console.log(`Making ${method} request to ${url}`);
      const response = await fetch(url, requestOptions);
      clearTimeout(timeoutId);

      console.log(`Response status: ${response.status} ${response.statusText}`);
      console.log(`Response headers:`, Object.fromEntries([...response.headers.entries()]));

      // Handle HTTP errors
      if (!response.ok) {
        let errorData = {};
        let responseText = '';

        try {
            // First get the raw text
            responseText = await response.text();
            console.log(`Raw error response: ${responseText.substring(0, 200)}${responseText.length > 200 ? '...' : ''}`);

            // Then try to parse as JSON
            try {
                errorData = JSON.parse(responseText);
                console.log(`Parsed error data:`, errorData);
            } catch (jsonError) {
                console.error(`Error parsing JSON response: ${jsonError}`);
                errorData = { message: responseText || 'Unknown error' };
            }
        } catch (textError) {
            console.error(`Error reading response text: ${textError}`);
            errorData = { message: 'Failed to parse error response.' };
        }

        console.error(`API Error ${response.status}:`, errorData); // Log the error details
        throw {
          status: response.status,
          statusText: response.statusText,
          data: errorData, // Include parsed error data if available
          rawResponse: responseText.substring(0, 500) // Include part of the raw response for debugging
        };
      }

      // Handle empty response body for certain statuses (e.g., 204 No Content)
      if (response.status === 204) {
        console.log('Received 204 No Content response');
        return null; // Or return an empty object/success indicator as needed
      }

      // Parse JSON response for other successful requests
      try {
        // First get the raw text
        const responseText = await response.text();
        console.log(`Raw success response: ${responseText.substring(0, 200)}${responseText.length > 200 ? '...' : ''}`);

        // Then parse as JSON
        const responseData = JSON.parse(responseText);
        console.log(`Parsed response data:`, responseData);
        return responseData;
      } catch (e) {
        console.error(`Error parsing successful response: ${e}`);
        throw {
          status: response.status,
          statusText: 'JSON Parse Error',
          data: { message: 'Failed to parse successful response as JSON.' },
          error: e.toString()
        };
      }
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
    return apiClientInstance.post('/api/v1/market/analyze', {
      market_segment: marketSegment,
      business_preference: businessPreference
    });
  },

  // Business models
  getBusinessModels: () => {
    console.log("API Call: getBusinessModels"); // Added logging
    console.log("Calling correct endpoint: /api/v1/business/list");
    return apiClientInstance.get('/api/v1/business/list');
  },

  getBusinessModel: (modelId) => {
    console.log("API Call: getBusinessModel", { modelId }); // Added logging
    return apiClientInstance.get(`/api/v1/business/models/${modelId}`);
  },

  createBusinessModel: (modelData) => {
    console.log("API Call: createBusinessModel", modelData); // Added logging
    return apiClientInstance.post('/api/v1/business/models', modelData);
  },

  // Features
  getFeatures: (businessModelId) => {
    console.log("API Call: getFeatures", { businessModelId }); // Added logging
    return apiClientInstance.get('/api/v1/features', { business_model_id: businessModelId });
  },

  implementFeature: (featureId, options) => {
    console.log("API Call: implementFeature", { featureId, options }); // Added logging
    return apiClientInstance.post(`/api/v1/features/${featureId}/implement`, options);
  },

  // User authentication
  login: (email, password) => {
    console.log("API Call: login with email:", email); // Added logging (don't log password)

    // Check if the URL is correct
    const loginUrl = '/api/v1/auth/login';
    console.log("Login URL:", loginUrl);

    // Make the request with detailed error handling
    return apiClientInstance.post(loginUrl, { email, password })
      .catch(error => {
        console.error("Login request failed:", error);

        // Log more details about the error
        if (error.status) {
          console.error(`Status: ${error.status}, Status Text: ${error.statusText}`);
        }

        if (error.data) {
          console.error("Error data:", error.data);
        }

        throw error; // Re-throw the error for the component to handle
      });
  },

  signup: (userData) => {
    console.log("API Call: signup with email:", userData.email); // Added logging (don't log password)

    // Check if the URL is correct
    const signupUrl = '/api/v1/auth/signup';
    console.log("Signup URL:", signupUrl);

    // Make the request with detailed error handling
    return apiClientInstance.post(signupUrl, userData)
      .catch(error => {
        console.error("Signup request failed:", error);

        // Log more details about the error
        if (error.status) {
          console.error(`Status: ${error.status}, Status Text: ${error.statusText}`);
        }

        if (error.data) {
          console.error("Error data:", error.data);
        }

        // Check for specific error conditions
        if (error.status === 409 || (error.data && error.data.message && error.data.message.includes('already registered'))) {
          console.log("Email already registered error detected");
          // Enhance the error object with a more specific status if the backend didn't provide it
          if (error.status !== 409) {
            error.status = 409;
          }
        }

        throw error; // Re-throw the error for the component to handle
      });
  },

  logout: () => {
    console.log("API Call: logout"); // Added logging
    return apiClientInstance.post('/api/v1/auth/logout');
  },

  getCurrentUser: () => {
    console.log("API Call: getCurrentUser"); // Added logging
    console.log("Token in localStorage:", localStorage.getItem('authToken') ? "Present" : "Missing");

    // Log the full URL being requested
    const fullUrl = `${apiClientInstance.baseUrl}/api/v1/auth/profile`;
    console.log("Full URL for getCurrentUser:", fullUrl);

    return apiClientInstance.get('/api/v1/auth/profile')
      .then(response => {
        console.log("getCurrentUser successful response:", response);
        return response;
      })
      .catch(error => {
        console.error("getCurrentUser error:", error);
        console.error("Error details:", error.status, error.statusText);
        if (error.data) {
          console.error("Error data:", error.data);
        }
        throw error;
      });
  },

  // OAuth authentication - Removed Google Sign-In
  loginWithGithub: (data) => {
    console.log("API Call: loginWithGithub"); // Added logging
    return apiClientInstance.post('/api/v1/auth/github', data);
  },

  // Subscription management
  getSubscriptionPlans: () => {
    console.log("API Call: getSubscriptionPlans"); // Added logging
    return apiClientInstance.get('/api/v1/subscriptions/plans');
  },

  getCurrentSubscription: () => {
    console.log("API Call: getCurrentSubscription"); // Added logging
    return apiClientInstance.get('/api/v1/subscriptions/current');
  },

  createCheckoutSession: (data) => {
    console.log("API Call: createCheckoutSession", data); // Added logging
    return apiClientInstance.post('/api/v1/subscriptions/create-checkout-session', data);
  },

  updateSubscription: (subscriptionId, data) => {
    console.log("API Call: updateSubscription", { subscriptionId, data }); // Added logging
    return apiClientInstance.put(`/api/v1/subscriptions/${subscriptionId}`, data);
  },

  cancelSubscription: (subscriptionId) => {
    console.log("API Call: cancelSubscription", { subscriptionId }); // Added logging
    return apiClientInstance.post(`/api/v1/subscriptions/${subscriptionId}/cancel`);
  },

  reactivateSubscription: (subscriptionId) => {
    console.log("API Call: reactivateSubscription", { subscriptionId }); // Added logging
    return apiClientInstance.post(`/api/v1/subscriptions/${subscriptionId}/reactivate`);
  },

  // System health and configuration
  getHealthStatus: () => {
    console.log("API Call: getHealthStatus"); // Added logging
    return apiClientInstance.get('/api/v1/health');
  },

  getConfig: () => {
    console.log("API Call: getConfig"); // Added logging
    return apiClientInstance.get('/api/v1/config');
  },

  // Workflows
  getWorkflows: () => {
    console.log("API Call: getWorkflows");
    return apiClientInstance.get('/api/v1/workflows');
  },

  createWorkflow: (workflowData) => {
    console.log("API Call: createWorkflow", workflowData);
    return apiClientInstance.post('/api/v1/workflows', workflowData);
  },

  // Cashflow
  getCashflowForecast: (businessId) => {
    console.log("API Call: getCashflowForecast", { businessId });
    return apiClientInstance.get(`/api/v1/cashflow/forecast/${businessId}`);
  },


  // Analytics
  getAnalyticsData: () => {
    console.log("API Call: getAnalyticsData");
    // Assuming an endpoint like /api/analytics will exist
    return apiClientInstance.get('/api/v1/analytics');
  }, // Comma after getAnalyticsData

  // Insights
  getInsightsData: () => {
    console.log("API Call: getInsightsData");
    // Assuming an endpoint like /api/insights will exist
    return apiClientInstance.get('/api/v1/insights');
  } // No comma after getInsightsData as it's the last item
,

  // Customers (Placeholder)
  getCustomersData: () => {
    console.log("API Call: getCustomersData (Placeholder)");
    // Assuming an endpoint like /api/customers will exist
    return apiClientInstance.get('/api/v1/customers');
  }
,

  // Revenue (Placeholder)
  getRevenueData: () => {
    console.log("API Call: getRevenueData (Placeholder)");
    // Assuming an endpoint like /api/revenue will exist
    return apiClientInstance.get('/api/v1/revenue');
  }
,

  // Orchestrator Tasks
  submitOrchestratorTask: (goal, parameters = {}) => {
    console.log("API Call: submitOrchestratorTask", { goal, parameters });
    return apiClientInstance.post('/api/v1/orchestrator/tasks', { goal, parameters });
  },

  // Agent Orchestration
  orchestrateAgents: (prompt, userId = null) => {
    console.log("API Call: orchestrateAgents", { prompt, userId });
    return apiClientInstance.post('/api/v1/agents/orchestrate', { prompt, user_id: userId });
  },

  // Workflow Resume
  resumeWorkflow: (workflowRunId, decision) => {
    console.log("API Call: resumeWorkflow", { workflowRunId, decision });
    return apiClientInstance.post(`/api/v1/a2a/workflow/${workflowRunId}/resume`, { decision });
  }
}; // Closing brace for apiService object
// Export the service object for use in components
export default apiService;