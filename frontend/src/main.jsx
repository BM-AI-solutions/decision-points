import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import '../css/styles.css'; // Keep existing styles for now
import './animations.js'; // Import animations

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);