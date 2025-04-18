import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';

const DashboardLayout = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true;
    console.log("DashboardLayout: Mounting component and checking authentication");
    
    // Check if token exists in localStorage
    const token = localStorage.getItem('authToken');
    console.log("DashboardLayout: Auth token exists in localStorage:", !!token);
    if (token) {
      console.log("DashboardLayout: Token from localStorage:", token.substring(0, 10) + "...");
    }
    
    apiService.getCurrentUser()
      .then((response) => {
        console.log("DashboardLayout: getCurrentUser successful response:", response);
        if (isMounted) {
          console.log("DashboardLayout: Setting authenticated to true");
          setAuthenticated(true);
          setLoading(false);
        }
      })
      .catch((error) => {
        console.error("DashboardLayout: getCurrentUser error:", error);
        if (isMounted) {
          console.log("DashboardLayout: Setting authenticated to false");
          setAuthenticated(false);
          setLoading(false);
          console.log("DashboardLayout: Redirecting to home page");
          navigate('/', { replace: true });
        }
      });
    return () => {
      console.log("DashboardLayout: Unmounting component");
      isMounted = false;
    };
  }, [navigate]);

  if (loading) {
    return <div style={{ textAlign: 'center', marginTop: '2rem' }}>Loading...</div>;
  }

  if (!authenticated) {
    return null; // Redirecting
  }

  return (
    <div className="dashboard-layout">
      {children}
    </div>
  );
};

export default DashboardLayout;