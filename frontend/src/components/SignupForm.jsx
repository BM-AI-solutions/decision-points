import React, { useState } from 'react';
import apiService from '../services/api.js'; // Import the API service

function SignupForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleSubmit = async (event) => { // Make the handler async
    event.preventDefault();
    // Remove the previous console log
    // Note: We are only sending email and password as per instructions
    const userData = { email, password };
    // Check deployment mode
    if (import.meta.env.VITE_DEPLOYMENT_MODE === 'cloud') {
      console.log('Cloud deployment detected: Proceeding with free tier signup.');
    } else {
      console.log('Self-hosted deployment detected: Proceeding with standard signup.');
    }


    try {
      const response = await apiService.signup(userData); // Call the signup API
      console.log('Signup successful:', response); // Log success response
    } catch (error) {
      console.error('Signup failed:', error); // Log any errors
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="signup-email">Email:</label>
        <input
          type="email"
          id="signup-email"
          name="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="signup-password">Password:</label>
        <input
          type="password"
          id="signup-password"
          name="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="confirm-password">Confirm Password:</label>
        <input
          type="password"
          id="confirm-password"
          name="confirmPassword"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
        />
      </div>
      <button type="submit">Sign Up</button>
    </form>
  );
}

export default SignupForm;