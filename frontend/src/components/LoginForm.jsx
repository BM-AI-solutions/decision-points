import React, { useState, useEffect } from 'react';
import apiService from '../services/api.js'; // Import the API service

function LoginForm({ onAuthSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isLocalDev, setIsLocalDev] = useState(false);

  useEffect(() => {
    // Check if we're in local development environment
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '';
    setIsLocalDev(apiBaseUrl.includes('localhost') || apiBaseUrl.includes('127.0.0.1'));

    // Pre-fill with test credentials in local dev mode
    if (apiBaseUrl.includes('localhost') || apiBaseUrl.includes('127.0.0.1')) {
      setEmail('test@example.com');
      setPassword('password123');
    }
  }, []);

  const handleSubmit = async (event) => {
    console.log('LoginForm handleSubmit triggered');
    event.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      console.log('Attempting login with email:', email);
      const response = await apiService.login(email, password);
      console.log('Login successful:', response);

      // Check if response has the expected structure
      if (response && response.success && response.token && response.user) {
        console.log('Valid login response received');
        // Store token in localStorage
        localStorage.setItem('authToken', response.token);
        // Store user info
        localStorage.setItem('user', JSON.stringify(response.user));
        // Notify parent (Header) of successful login
        if (onAuthSuccess) {
          onAuthSuccess(response.user);
        }
        window.location.href = '/dashboard'; // Redirect to dashboard or home page
      } else {
        console.error('Invalid response structure:', response);
        setError('Login failed. Received invalid response from server.');
      }
    } catch (error) {
      console.error('Login failed:', error);
      const errorMessage = error.data?.message || 'Please check your credentials and try again.';
      setError(`Login failed. ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-form-container">
      {error && <div className="auth-error">{error}</div>}

      {isLocalDev && (
        <div className="dev-notice" style={{ background: '#f0f8ff', padding: '10px', borderRadius: '5px', marginBottom: '15px', fontSize: '14px' }}>
          <strong>Local Development Mode</strong>
          <p style={{ margin: '5px 0' }}>Default test credentials have been pre-filled:</p>
          <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
            <li>Email: test@example.com</li>
            <li>Password: password123</li>
          </ul>
        </div>
      )}

      <form onSubmit={handleSubmit} className="auth-form">
        <div className="form-group">
          <label htmlFor="login-email" className="form-label">Email</label>
          <div className="input-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="input-icon">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
              <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
            <input
              type="email"
              id="login-email"
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
          <label htmlFor="login-password" className="form-label">Password</label>
          <div className="input-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="input-icon">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <input
              type="password"
              id="login-password"
              name="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
        </div>

        <div className="form-footer">
          <div className="remember-me">
            <input type="checkbox" id="remember-me" />
            <label htmlFor="remember-me">Remember me</label>
          </div>
          <a href="#" className="forgot-password">Forgot password?</a>
        </div>

        <button
          type="submit"
          className={`btn btn-primary btn-full ${isLoading ? 'btn-loading' : ''}`}
          disabled={isLoading}
        >
          {isLoading ? 'Logging in...' : 'Log In'}
        </button>
      </form>


    </div>
  );
}

export default LoginForm;