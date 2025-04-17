import React, { useState } from 'react';
import apiService from '../services/api.js'; // Import the API service

function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (event) => { // Make the handler async
    event.preventDefault();
    // Remove the previous console log
    try {
      const response = await apiService.login(email, password); // Call the login API
      console.log('Login successful:', response); // Log success response
    } catch (error) {
      console.error('Login failed:', error); // Log any errors
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="login-email">Email:</label>
        <input
          type="email"
          id="login-email"
          name="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="login-password">Password:</label>
        <input
          type="password"
          id="login-password"
          name="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>
      <button type="submit">Log In</button>
    </form>
  );
}

export default LoginForm;