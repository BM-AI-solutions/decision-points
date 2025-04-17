import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';

const DashboardLayout = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true;
    apiService.getCurrentUser()
      .then(() => {
        if (isMounted) {
          setAuthenticated(true);
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setAuthenticated(false);
          setLoading(false);
          navigate('/', { replace: true });
        }
      });
    return () => { isMounted = false; };
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