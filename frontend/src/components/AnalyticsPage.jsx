import React, { useState, useEffect } from 'react';
import apiService from '../services/api'; // Import the apiService

const AnalyticsPage = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Use the new API function
        const data = await apiService.getAnalyticsData();
        setAnalyticsData(data);
        console.log("Fetched analytics data:", data); // Log fetched data
      } catch (err) {
        console.error("Error fetching analytics data:", err);
        // Handle potential error structures
        const errorMessage = err?.data?.message || err?.statusText || 'Failed to fetch analytics data.';
        setError(errorMessage);
        setAnalyticsData(null); // Clear data on error
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []); // Empty dependency array ensures this runs only once on mount

  return (
    <div style={{ padding: '40px', color: '#fff' }}>
      <h1>Analytics Page</h1>

      {loading && <p>Loading analytics data...</p>}

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {analyticsData && !loading && !error && (
        <div>
          <h2>Key Metrics</h2>
          {/* Display fetched data - Adjust based on actual data structure */}
          {/* Example: Assuming data is an object with key-value pairs */}
          {typeof analyticsData === 'object' && analyticsData !== null ? (
            <ul>
              {Object.entries(analyticsData).map(([key, value]) => (
                <li key={key}><strong>{key}:</strong> {JSON.stringify(value)}</li>
              ))}
            </ul>
          ) : (
            <pre>{JSON.stringify(analyticsData, null, 2)}</pre>
          )}
          <p><em>Note: Display format is basic. Actual data structure from the backend API is needed for better presentation.</em></p>
        </div>
      )}

      {!loading && !error && !analyticsData && (
         <p>No analytics data available.</p>
      )}
    </div>
  );
};

export default AnalyticsPage;