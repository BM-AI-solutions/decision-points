import styles from './LoginForm.module.css';
import React, { useState } from 'react';
import apiService from '../services/api.js'; // Import the API service

function LoginForm({ onAuthSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {

    event.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {

      const response = await apiService.login(email, password);

      // Check if response has the expected structure
      if (response && response.success && response.token && response.user) {

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
    <div className={styles.authFormContainer}>
      {error && <div className={styles.authError}>{error}</div>}
      
      <form onSubmit={handleSubmit} className={styles.authForm}>
        <div className={styles.formGroup}>
          <label htmlFor="login-email" className={styles.formLabel}>Email</label>
          <div className={styles.inputWrapper}>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={styles.inputIcon}>
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
              <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
            <input
              type="email"
              id="login-email"
              name="email"
              className={styles.formInput}
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
        </div>
        
        <div className={styles.formGroup}>
          <label htmlFor="login-password" className={styles.formLabel}>Password</label>
          <div className={styles.inputWrapper}>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={styles.inputIcon}>
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <input
              type="password"
              id="login-password"
              name="password"
              className={styles.formInput}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
        </div>
        
        <div className={styles.formFooter}>
          <div className={styles.rememberMe}>
            <input type="checkbox" id="remember-me" />
            <label htmlFor="remember-me">Remember me</label>
          </div>
          <a href="#" className={styles.forgotPassword}>Forgot password?</a>
        </div>
        
        <button
          type="submit"
          className={`btn btn-primary btn-full ${isLoading ? styles.btnLoading : ''}`}
          disabled={isLoading}
        >
          {isLoading ? 'Logging in...' : 'Log In'}
        </button>
      </form>
      
      <div className={styles.authDivider}>
        <span>OR</span>
      </div>
      
      <div className={styles.socialLogin}>
        <button className="btn btn-social btn-google">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/>
          </svg>
          Continue with Google
        </button>
      </div>
    </div>
  );
}

export default LoginForm;