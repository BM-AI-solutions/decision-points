import React, { useEffect, useState } from 'react';
import { useNavigate, NavLink } from 'react-router-dom';
import apiService from '../services/api';

const DashboardLayout = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true;
    console.log("DashboardLayout: Mounting component and checking authentication");

    const token = localStorage.getItem('authToken');
    console.log("DashboardLayout: Auth token exists in localStorage:", !!token);
    if (!token) {
        console.log("DashboardLayout: No token found, redirecting to home");
        navigate('/', { replace: true });
        setLoading(false);
        return;
    }
    console.log("DashboardLayout: Token from localStorage:", token.substring(0, 10) + "...");

    apiService.getCurrentUser()
      .then((response) => {
        console.log("DashboardLayout: getCurrentUser successful response:", response);
        if (isMounted && response?.success && response?.user) {
          console.log("DashboardLayout: Setting authenticated to true and storing user");
          setAuthenticated(true);
          setUser(response.user);
          setLoading(false);
        } else if (isMounted) {
           console.log("DashboardLayout: API success but no user data, setting authenticated to false");
           setAuthenticated(false);
           setLoading(false);
           localStorage.removeItem('authToken');
           navigate('/', { replace: true });
        }
      })
      .catch((error) => {
        console.error("DashboardLayout: getCurrentUser error:", error);
        if (isMounted) {
          console.log("DashboardLayout: Setting authenticated to false due to error");
          setAuthenticated(false);
          setLoading(false);
          localStorage.removeItem('authToken');
          console.log("DashboardLayout: Redirecting to home page");
          navigate('/', { replace: true });
        }
      });
    return () => {
      console.log("DashboardLayout: Unmounting component");
      isMounted = false;
    };
  }, [navigate]);

  const handleLogout = () => {
    apiService.logout();
    navigate('/');
  };

  // Sidebar links data
  const sidebarLinks = [
    { label: 'Dashboard', icon: 'fas fa-home', route: '/dashboard' },
    { label: 'Analytics', icon: 'fas fa-chart-pie', route: '/dashboard/analytics' },
    { label: 'Automation', icon: 'fas fa-cogs', route: '/dashboard/automation' },
    { label: 'Insights', icon: 'fas fa-lightbulb', route: '/dashboard/insights' },
    { label: 'Customers', icon: 'fas fa-users', route: '/dashboard/customers' },
    { label: 'Revenue', icon: 'fas fa-dollar-sign', route: '/dashboard/revenue' },
  ];

  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#0D0D0D', color: '#fff' }}>Loading Dashboard...</div>;
  }

  if (!authenticated) {
    return null;
  }

  return (
    <div style={{ width: '100%', height: '100vh', display: 'flex', flexDirection: 'column', background: '#0D0D0D', color: '#fff' }}>
      {/* Header */}
      <div style={{
        height: '65px',
        background: 'rgba(10, 10, 10, 0.95)',
        borderBottom: '1px solid rgba(255, 71, 19, 0.2)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '0 25px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)',
        position: 'relative'
      }}>
        {/* Decorative header gradient */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '2px',
          background: 'linear-gradient(90deg, #ff4713, #d90429, #ff4713)',
          backgroundSize: '200% 200%'
        }}></div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          fontWeight: 'bold',
          fontSize: '20px',
          color: '#ff4713',
          textShadow: '0 2px 4px rgba(255, 71, 19, 0.3)'
        }}>
          <i className="fas fa-fire" style={{
            fontSize: '22px',
            filter: 'drop-shadow(0 2px 4px rgba(255, 71, 19, 0.5))'
          }}></i>
          Decision Points AI
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '25px'
        }}>
          <i className="fas fa-bell" style={{
            cursor: 'pointer',
            color: 'rgba(255, 255, 255, 0.7)',
            transition: 'all 0.2s ease',
            fontSize: '18px'
          }}></i>
          <i className="fas fa-cog" style={{
            cursor: 'pointer',
            color: 'rgba(255, 255, 255, 0.7)',
            transition: 'all 0.2s ease',
            fontSize: '18px'
          }}></i>
          {user ? (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '15px',
              background: 'rgba(30, 0, 0, 0.4)',
              padding: '6px 8px 6px 15px',
              borderRadius: '30px',
              border: '1px solid rgba(255, 71, 19, 0.2)',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
            }}>
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #ff4713, #d90429)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: 'bold',
                color: '#fff',
                boxShadow: '0 2px 6px rgba(255, 71, 19, 0.3)'
              }}>
                {user.email.charAt(0).toUpperCase()}
              </div>
              <span style={{
                fontSize: '14px',
                fontWeight: '500'
              }}>{user.email}</span>
              <button
                onClick={handleLogout}
                style={{
                  background: 'linear-gradient(135deg, #ff4713, #d90429)',
                  border: 'none',
                  color: '#fff',
                  padding: '8px 15px',
                  borderRadius: '20px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500',
                  boxShadow: '0 2px 6px rgba(255, 71, 19, 0.3)',
                  transition: 'all 0.2s ease'
                }}
              >
                Logout
              </button>
            </div>
          ) : (
            <i className="fas fa-user-circle" style={{
              color: 'rgba(255, 255, 255, 0.7)',
              fontSize: '20px'
            }}></i>
          )}
        </div>
      </div>

      {/* Main Content Area with Sidebar */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Sidebar */}
        <div style={{
          width: '220px',
          background: 'rgba(8, 8, 8, 0.95)',
          borderRight: '1px solid rgba(255, 71, 19, 0.1)',
          display: 'flex',
          flexDirection: 'column',
          padding: '25px 0',
          boxShadow: '4px 0 20px rgba(0, 0, 0, 0.3)',
          position: 'relative'
        }}>
          {/* Sidebar gradient accent */}
          <div style={{
            position: 'absolute',
            top: 0,
            bottom: 0,
            left: 0,
            width: '2px',
            background: 'linear-gradient(180deg, #ff4713, #d90429, transparent)',
            opacity: 0.7
          }}></div>
          {sidebarLinks.map((link, idx) => (
            <NavLink
              key={link.label}
              to={link.route}
              end={link.route === '/dashboard'} // Ensure exact match for the main dashboard link
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '14px 25px',
                color: isActive ? '#ff4713' : 'rgba(255, 255, 255, 0.7)',
                background: isActive ? 'rgba(255, 71, 19, 0.1)' : 'transparent',
                borderLeft: isActive ? '3px solid #ff4713' : '3px solid transparent',
                textDecoration: 'none',
                transition: 'all 0.2s ease',
                position: 'relative',
                marginBottom: '5px',
                fontSize: '15px',
                fontWeight: isActive ? '600' : '400'
              })}
            >
              {({ isActive }) => (
                <>
                  <div style={{
                    width: '32px',
                    height: '32px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: '8px',
                    background: isActive ?
                      'linear-gradient(135deg, rgba(255, 71, 19, 0.2), rgba(217, 4, 41, 0.2))' :
                      'transparent',
                    boxShadow: isActive ?
                      '0 2px 8px rgba(255, 71, 19, 0.2)' :
                      'none'
                  }}>
                    <i className={link.icon} style={{
                      fontSize: '16px',
                      color: isActive ? '#ff4713' : 'rgba(255, 255, 255, 0.7)'
                    }}></i>
                  </div>
                  {link.label}
                  
                  {/* Active indicator dot */}
                  {isActive && (
                    <div style={{
                      position: 'absolute',
                      right: '20px',
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      background: '#ff4713'
                    }}></div>
                  )}
                </>
              )}
            </NavLink>
          ))}
        </div>

        {/* Main Content */}
        <div style={{
          flex: 1,
          overflow: 'auto',
          background: 'linear-gradient(135deg, #0D0D0D 0%, #260101 50%, #570111 100%)',
          backgroundSize: '200% 200%',
          position: 'relative'
        }}>
          {/* Decorative background elements */}
          <div style={{
            position: 'absolute',
            top: '5%',
            right: '5%',
            width: '300px',
            height: '300px',
            background: 'radial-gradient(circle, rgba(255, 71, 19, 0.05) 0%, rgba(255, 71, 19, 0) 70%)',
            borderRadius: '50%',
            opacity: 0.6,
            zIndex: 0,
            pointerEvents: 'none'
          }}></div>
          <div style={{
            position: 'absolute',
            bottom: '10%',
            left: '5%',
            width: '250px',
            height: '250px',
            background: 'radial-gradient(circle, rgba(59, 130, 246, 0.05) 0%, rgba(59, 130, 246, 0) 70%)',
            borderRadius: '50%',
            opacity: 0.6,
            zIndex: 0,
            pointerEvents: 'none'
          }}></div>
          {children}
        </div>
      </div>
    </div>
  );
};

export default DashboardLayout;