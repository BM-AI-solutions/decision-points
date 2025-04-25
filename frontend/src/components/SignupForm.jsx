import React, { useState } from 'react';
import apiService from '../services/api.js'; // Import the API service

function SignupForm({ onAuthSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    console.log('SignupForm handleSubmit triggered');
    event.preventDefault();
    
    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    // Note: We are only sending email and password as per instructions
    const userData = { email, password };
    
    // Check deployment mode
    if (import.meta.env.VITE_DEPLOYMENT_MODE === 'cloud') {
      console.log('Cloud deployment detected: Proceeding with free tier signup.');
    } else {
      console.log('Self-hosted deployment detected: Proceeding with standard signup.');
    }

    try {
      const response = await apiService.signup(userData);
      console.log('Signup successful:', response);
      
      // Store token and user info
      if (response && response.success && response.token && response.user) {
        localStorage.setItem('authToken', response.token);
        localStorage.setItem('user', JSON.stringify(response.user));
        // Notify parent (Header) of successful signup
        if (onAuthSuccess) {
          onAuthSuccess(response.user);
        }
        // Redirect to dashboard or home page
        window.location.href = '/dashboard';
      }
    } catch (error) {
      console.error('Signup failed:', error);

      let errorMessage = 'An unexpected error occurred. Please try again.';

      if (error.response) {
        // Attempt to parse the response body as JSON
        try {
          const errorData = error.response.data;
          if (errorData && typeof errorData === 'object' && errorData.message) {
            errorMessage = errorData.message;
          } else {
            // If JSON is present but doesn't match the expected format
            errorMessage = 'Signup failed: Invalid error response from server.';
          }
        } catch (parseError) {
          // If response body is not valid JSON
          errorMessage = 'Signup failed: Received non-JSON error response from server.';
        }
      } else {
        // Handle network errors or other issues without a response
        errorMessage = 'Signup failed: Could not connect to the server.';
      }

      setError(errorMessage);

    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-form-container">
      {error && <div className="auth-error">{error}</div>}
      
      <form onSubmit={handleSubmit} className="auth-form">
        <div className="form-group">
          <label htmlFor="signup-email" className="form-label">Email</label>
          <div className="input-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="input-icon">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
              <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
            <input
              type="email"
              id="signup-email"
              name="email"
              className="form-input"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="signup-password" className="form-label">Password</label>
          <div className="input-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="input-icon">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <input
              type="password"
              id="signup-password"
              name="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="confirm-password" className="form-label">Confirm Password</label>
          <div className="input-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="input-icon">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <input
              type="password"
              id="confirm-password"
              name="confirmPassword"
              className="form-input"
              placeholder="••••••••"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>
        </div>
        
        <div className="terms-agreement">
          <input type="checkbox" id="terms-agreement" required />
          <label htmlFor="terms-agreement">I agree to the <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a></label>
        </div>
        
        <button
          type="submit"
          className={`btn btn-primary btn-full ${isLoading ? 'btn-loading' : ''}`}
          disabled={isLoading}
        >
          {isLoading ? 'Creating Account...' : 'Sign Up'}
        </button>
      </form>
      
      <div className="auth-divider">
        <span>OR</span>
      </div>
    </div>
  );
}

export default SignupForm;