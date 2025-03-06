/**
 * Cloudflare Worker script to proxy API requests to the Decision Points backend
 * 
 * This worker handles:
 * 1. API request proxying to Google Cloud Functions
 * 2. CORS headers
 * 3. API key validation
 * 4. Rate limiting
 * 5. Request logging
 */

// Configuration
const API_HOST = 'us-central1-single-bindery-452721-n8.cloudfunctions.net';  // Your GCF hostname - replace YOUR_PROJECT_ID with your actual GCP project ID
const API_PATH = '/intellisol-api';  // Cloud Function name/path
const ALLOWED_ORIGINS = ['https://intellisol.cc', 'https://decisionpoints.intellisol.cc'];
const REQUIRE_API_KEY = false;  // Set to true to require API key for all requests

// Rate limiting (using Cloudflare's built-in features)
const RATE_LIMIT = {
  max_requests: 100,  // Maximum requests per time window
  time_window: 60,    // Time window in seconds
};

// API endpoints that don't require authentication (public endpoints)
const PUBLIC_ENDPOINTS = [
  '/api/health',
  '/api/config',
  '/api/auth/google'
];

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event));
});

async function handleRequest(event) {
  const request = event.request;
  const url = new URL(request.url);

  // Handle CORS preflight requests
  if (request.method === 'OPTIONS') {
    return handleCORS(request);
  }

  // Check if the path is for the API
  if (url.pathname.startsWith('/api/')) {
    // Handle API requests
    return handleAPIRequest(request, event);
  } else {
    // Serve static assets or redirect to the main app
    return handleStaticOrRedirect(request);
  }
}

async function handleAPIRequest(request, event) {
  const url = new URL(request.url);
  const originalPath = url.pathname;

  // Check if the endpoint requires authentication
  const isPublicEndpoint = PUBLIC_ENDPOINTS.some(endpoint => originalPath.startsWith(endpoint));

  if (REQUIRE_API_KEY && !isPublicEndpoint) {
    // Validate API key (if required)
    const apiKey = request.headers.get('X-API-Key');
    if (!apiKey) {
      return jsonResponse({ error: 'API key is required' }, 401);
    }

    // You would typically validate the API key against your database
    // For this example, we're skipping actual validation
  }

  // Check rate limiting (if not using Cloudflare's rate limiting features)
  // This is a simplified example - Cloudflare has built-in rate limiting that's more robust
  if (!isPublicEndpoint) {
    const clientIP = request.headers.get('CF-Connecting-IP');
    const rateLimitKey = `ratelimit:${clientIP}:${originalPath}`;

    // In a real implementation, you would check and increment a counter in KV storage
    // For this example, we're skipping actual rate limiting checks
  }

  // Forward the request to the backend API
  // Transform the path to work with Cloud Functions
  const gcfPath = url.pathname.replace('/api', API_PATH);
  const apiURL = new URL(`https://${API_HOST}${gcfPath}${url.search}`);

  // Clone the request with the new URL
  const apiRequest = new Request(apiURL.toString(), {
    method: request.method,
    headers: request.headers,
    body: request.body,
    redirect: 'follow'
  });

  try {
    // Fetch from the backend API
    const response = await fetch(apiRequest);

    // Clone the response and add CORS headers
    const newResponse = new Response(response.body, response);
    addCORSHeaders(newResponse, request);

    // Log the request (if needed)
    // In a production environment, you might want to log only certain requests
    // or send logs to a logging service

    return newResponse;
  } catch (error) {
    // Handle errors
    return jsonResponse({ 
      error: 'API request failed', 
      message: error.message 
    }, 500);
  }
}

function handleStaticOrRedirect(request) {
  const url = new URL(request.url);

  // Redirect to the main app for most paths
  if (url.pathname === '/' || url.pathname === '/index.html') {
    return fetch(request);
  } else {
    // Try to serve static assets
    return fetch(request)
      .then(response => {
        if (response.status === 404) {
          // If the asset is not found, redirect to the main app
          return Response.redirect('/', 302);
        }
        return response;
      })
      .catch(error => {
        return Response.redirect('/', 302);
      });
  }
}

function handleCORS(request) {
  // Create a new response for CORS preflight requests
  const response = new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': getAllowedOrigin(request),
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
      'Access-Control-Max-Age': '86400',
    }
  });

  return response;
}

function addCORSHeaders(response, request) {
  response.headers.set('Access-Control-Allow-Origin', getAllowedOrigin(request));
  return response;
}

function getAllowedOrigin(request) {
  const origin = request.headers.get('Origin');

  // Check if the origin is in the allowed list
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    return origin;
  }

  // Default to the first allowed origin
  return ALLOWED_ORIGINS[0];
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    }
  });
}
