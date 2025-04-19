import React, { useState, useEffect } from 'react';
import apiService from '../services/api.js'; // Corrected import path

const CustomersPage = () => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCustomers = async () => {
      setLoading(true);
      setError(null);
      try {
        // Use the placeholder API function
        const data = await apiService.getCustomersData();
        // Assuming the API returns an array of customers under a 'customers' key
        // Adjust based on actual API response structure if available later
        setCustomers(data.customers || []);

      } catch (err) {
        console.error("Error fetching customers:", err);
        // Handle specific error messages if available
        const errorMessage = err.data?.message || err.message || 'Failed to fetch customer data. The backend endpoint might be missing or return an error.';
        setError(errorMessage);
        setCustomers([]); // Clear customers on error
      } finally {
        setLoading(false);
      }
    };

    fetchCustomers();
  }, []); // Empty dependency array ensures this runs only once on mount

  return (
    <div style={{ padding: '40px', color: '#fff' }}>
      <h1>Customers Page</h1>

      {loading && <p>Loading customer data...</p>}

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {!loading && !error && (
        <div>
          {customers.length > 0 ? (
            <table>
              <thead>
                <tr>
                  {/* Adjust headers based on actual customer data structure */}
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  {/* Add more headers as needed */}
                </tr>
              </thead>
              <tbody>
                {customers.map((customer) => (
                  <tr key={customer.id}>
                    {/* Adjust data access based on actual customer object structure */}
                    <td>{customer.id || 'N/A'}</td>
                    <td>{customer.name || 'N/A'}</td>
                    <td>{customer.email || 'N/A'}</td>
                    {/* Add more cells as needed */}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No customer data available. The backend might not be returning data yet.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default CustomersPage;