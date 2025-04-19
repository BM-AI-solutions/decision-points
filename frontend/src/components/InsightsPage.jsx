import React, { useState, useEffect } from 'react';
import apiService from '../../services/api.js'; // Corrected path assuming InsightsPage is in components

const InsightsPage = () => {
  const [insightsData, setInsightsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInsights = async () => {
      setLoading(true);
      setError(null);
      try {
        // Use the placeholder API function
        const data = await apiService.getInsightsData();
        setInsightsData(data);

      } catch (err) {
        console.error("Error fetching insights:", err);
        // Handle potential error structure from ApiClient
        const errorMessage = err?.data?.message || err?.rawResponse || err?.statusText || 'Failed to fetch insights data.';
        setError(errorMessage);
        // Since the endpoint likely doesn't exist, we expect an error.
        // For now, let's set some placeholder data to show the structure.
        setInsightsData({
          trends: ["Trend A: Market Shift Towards X", "Trend B: Increased Demand for Y"],
          performance: {
            metric1: "Value 1",
            metric2: "Value 2"
          },
          message: "Note: Displaying placeholder data as backend endpoint is not yet available."
        });
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, []); // Empty dependency array ensures this runs only once on mount

  return (
    <div style={{ padding: '40px', color: '#fff', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ borderBottom: '2px solid #555', paddingBottom: '10px', marginBottom: '20px' }}>Insights</h1>

      {loading && <p>Loading insights...</p>}

      {error && <p style={{ color: '#ff6b6b', border: '1px solid #ff6b6b', padding: '10px', borderRadius: '4px' }}>Error: {error}</p>}

      {!loading && !error && insightsData && (
        <div>
          {insightsData.message && <p style={{ fontStyle: 'italic', color: '#ccc', marginBottom: '20px' }}>{insightsData.message}</p>}

          <h2 style={{ color: '#aaa', marginTop: '30px' }}>Market Trends</h2>
          {insightsData.trends && insightsData.trends.length > 0 ? (
            <ul style={{ listStyle: 'disc', paddingLeft: '20px' }}>
              {insightsData.trends.map((trend, index) => (
                <li key={index} style={{ marginBottom: '8px' }}>{trend}</li>
              ))}
            </ul>
          ) : (
            <p>No market trends data available.</p>
          )}

          <h2 style={{ color: '#aaa', marginTop: '30px' }}>Performance Insights</h2>
          {insightsData.performance ? (
            <ul style={{ listStyle: 'none', paddingLeft: '0' }}>
              {Object.entries(insightsData.performance).map(([key, value]) => (
                <li key={key} style={{ marginBottom: '8px' }}>
                  <strong style={{ textTransform: 'capitalize' }}>{key.replace(/([A-Z])/g, ' $1')}:</strong> {value}
                </li>
              ))}
            </ul>
          ) : (
            <p>No performance insights data available.</p>
          )}

          {/* You can add more sections here as needed */}

        </div>
      )}

      {!loading && !error && !insightsData && (
         <p>No insights data available.</p>
      )}
    </div>
  );
};

export default InsightsPage;