import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import LoginForm from './LoginForm'; // Import LoginForm
import SignupForm from './SignupForm'; // Import SignupForm

function Header() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userInfo, setUserInfo] = useState(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false); // State for mobile menu
  const [showLogin, setShowLogin] = useState(false); // State for login form visibility
  const [showSignup, setShowSignup] = useState(false); // State for signup form visibility
  const googleButtonRef = useRef(null); // Ref for the button container

  // Check localStorage for auth state on mount
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('user');
    if (token && user) {
      setIsLoggedIn(true);
      try {
        setUserInfo(JSON.parse(user));
      } catch {
        setUserInfo(null);
      }
    } else {
      setIsLoggedIn(false);
      setUserInfo(null);
    }
  }, []);

  // Toggle Mobile Menu
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen((prev) => {
      const next = !prev;

      return next;
    });
  };

  // Click Handlers for Login/Signup
  const handleLoginClick = () => {

    setShowLogin(true);
    setShowSignup(false);
    // Future implementation: Open login modal/form (State now handles visibility)
  };

  const handleSignupClick = () => {

    setShowSignup(true);
    setShowLogin(false);
    // Future implementation: Open signup modal/form (State now handles visibility)
  };

  // Smooth Scroll Handler
  const handleSmoothScroll = (event, targetId) => {
    event.preventDefault();
    const targetElement = document.querySelector(targetId);

    if (targetElement) {
      const yOffset = -80; // Adjust offset as needed (e.g., for fixed header height)
      const elementPosition = targetElement.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset + yOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });

      // Close mobile menu if open
      if (isMobileMenuOpen) {
        setIsMobileMenuOpen(false);
      }
    }
  };


  // Add/remove menu-open class on body when mobile menu is toggled
  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.classList.add('menu-open');
    } else {
      document.body.classList.remove('menu-open');
    }
    // Cleanup on unmount
    return () => document.body.classList.remove('menu-open');
  }, [isMobileMenuOpen]);

  // Handle the sign-in response
  const handleCredentialResponse = (response) => {

    if (response.credential) {
      try {
        // Basic decoding (for demonstration - use a library like jwt-decode in production)
        const base64Url = response.credential.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));

        const decodedToken = JSON.parse(jsonPayload);

        // Update state and persist to localStorage
        setIsLoggedIn(true);
        const userObj = {
          id: decodedToken.sub,
          name: decodedToken.name,
          email: decodedToken.email,
          picture: decodedToken.picture,
        };
        setUserInfo(userObj);
        localStorage.setItem('authToken', response.credential);
        localStorage.setItem('user', JSON.stringify(userObj));

        // TODO: Send token to backend for verification and session management

        // Simulate redirect or update UI further
        // alert(`Welcome, ${decodedToken.name}! (Sign-in successful, backend verification pending)`);

      } catch (error) {
        console.error("Error decoding credential or updating state:", error);
        setIsLoggedIn(false);
        setUserInfo(null);
        alert("Sign-in failed. Could not process credential.");
      }
    } else {
      console.error("No credential received in response.");
      alert("Sign-in failed. No credential received.");
    }
  };

  // Basic Logout Function
  const handleLogout = () => {
    // Clear localStorage and state
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    setIsLoggedIn(false);
    setUserInfo(null);
    setShowLogin(false);
    setShowSignup(false);

    // Ensure Google API is loaded before trying to re-render button
    if (window.google && window.google.accounts && googleButtonRef.current) {
        googleButtonRef.current.innerHTML = ''; // Clear old button/user info
        try {
            window.google.accounts.id.renderButton(
                googleButtonRef.current,
                {
                    type: "standard",
                    theme: "outline",
                    size: "large",
                    text: "signin_with",
                    shape: "rectangular",
                }
            );

        } catch (error) {
            console.error("Error rendering Google Sign-In button after logout:", error);
        }
    } else {

    }
    // Optionally redirect to home page
    window.location.href = '/';
  };

  useEffect(() => {
    // Function to load the Google GSI script
    const loadGoogleScript = () => {
      // Check if script already exists
      if (document.querySelector('script[src="https://accounts.google.com/gsi/client"]')) {

        // Check if the google object is ready
        if (window.google && window.google.accounts) {

            initializeGoogleSignIn(); // Initialize directly if script exists and client is ready
        } else {

            // If script exists but not ready, wait for it via onload (might already be loading)
            const existingScript = document.querySelector('script[src="https://accounts.google.com/gsi/client"]');
            if (existingScript && !existingScript.onload) { // Add onload if not already set
                 existingScript.onload = initializeGoogleSignIn;
            }
            // Or retry initialization after a delay as a fallback
            setTimeout(initializeGoogleSignIn, 200);
        }
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = () => {

          initializeGoogleSignIn();
      };
      script.onerror = () => console.error("Failed to load Google Sign-In API script");
      document.body.appendChild(script);
    };

    // Function to initialize Google Sign-In
    const initializeGoogleSignIn = () => {
      if (!window.google || !window.google.accounts || !window.google.accounts.id) {
        console.error("Google GSI client (google.accounts.id) not ready for initialization.");
        // Retry initialization after a short delay
        setTimeout(initializeGoogleSignIn, 150);
        return;
      }

      try {

        window.google.accounts.id.initialize({
          client_id: '706670564943-pmitiums8ciksifmpmio5v5dtcius8rd.apps.googleusercontent.com', // Use the same client ID
          callback: handleCredentialResponse,
          auto_select: false,
          cancel_on_tap_outside: true
        });

        // Render button only if user is not logged in
        if (!isLoggedIn) {
             renderGoogleButton();
        }
      } catch (error) {
        console.error("Error initializing Google Sign-In:", error);
      }
    };

    // Function to render the Google Sign-In button
    const renderGoogleButton = () => {
        // Delay rendering slightly to ensure DOM element is ready
        setTimeout(() => {
            if (!window.google || !window.google.accounts || !window.google.accounts.id) {

                // Optionally retry or log error
                return;
            }
            if (!googleButtonRef.current) {

                // Retry rendering after a short delay
                // setTimeout(renderGoogleButton, 100);
                return;
            }

            // Clear previous button if any
            googleButtonRef.current.innerHTML = '';
            try {
                window.google.accounts.id.renderButton(
                    googleButtonRef.current,
                    {
                        type: "standard",
                        theme: "outline", // Matches original style
                        size: "large",    // Matches original style
                        text: "signin_with", // Matches original style
                        shape: "rectangular", // Matches original style
                        // Consider setting width via CSS for better responsiveness
                        // width: "250" // Example fixed width
                    }
                );

            } catch (error) {
                console.error("Error rendering Google Sign-In button:", error);
            }
        }, 50); // Small delay for DOM readiness
    };

    loadGoogleScript();

    // Cleanup function (optional, see comments in original thought)
    return () => {
      // Optional cleanup logic here
    };
  // Rerun effect if isLoggedIn changes to re-render button correctly after logout
  }, [isLoggedIn]);

  return (
    <> {/* Use Fragment to return multiple elements */}
      <nav className="navbar">
        <div className="container">
          <div className="logo">
            <Link to="/">
              <img src="images/logo.svg" alt="Decision Points AI Logo" />
            </Link>
          </div>
          
          {/* Navigation menu with improved styling */}
          <ul className={isMobileMenuOpen ? 'nav-menu active' : 'nav-menu'}>
            <li>
              <a
                href="#features"
                className="nav-link"
                onClick={(e) => handleSmoothScroll(e, '#features')}
              >
                Features
              </a>
            </li>
            <li>
              <a
                href="#how-it-works"
                className="nav-link"
                onClick={(e) => handleSmoothScroll(e, '#how-it-works')}
              >
                How It Works
              </a>
            </li>
            <li>
              <a
                href="#pricing"
                className="nav-link"
                onClick={(e) => handleSmoothScroll(e, '#pricing')}
              >
                Pricing
              </a>
            </li>
            <li>
              <a
                href="#app"
                className="nav-link"
                onClick={(e) => handleSmoothScroll(e, '#app')}
              >
                Start Building
              </a>
            </li>
            <li>
              <a
                href="#testimonials"
                className="nav-link"
                onClick={(e) => handleSmoothScroll(e, '#testimonials')}
              >
                Testimonials
              </a>
            </li>
            {isLoggedIn && (
              <li>
                <Link
                  to="/dashboard"
                  className="nav-link"
                >
                  Dashboard
                </Link>
              </li>
            )}
            <li className="auth-item">
              {isLoggedIn ? (
                <div className="user-info">
                  {userInfo?.picture && (
                    <img
                      src={userInfo.picture}
                      alt={userInfo.name || 'User'}
                      className="user-avatar"
                    />
                  )}
                  <span className="user-name">{userInfo?.name || userInfo?.email || 'User'}</span>
                  <button
                    onClick={handleLogout}
                    className="btn btn-secondary logout-btn"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                // Container for the Login/Signup buttons
                <div className="auth-buttons-container">
                  <button className="btn btn-secondary btn-login" style={{ marginRight: '10px' }} onClick={handleLoginClick}>Log in</button>
                  <button className="btn btn-primary btn-signup" onClick={handleSignupClick}>Sign up</button>
                </div>
              )}
            </li>
          </ul>
          
          {/* Mobile menu toggle button with SVG icon instead of Font Awesome */}
          <button
            className="navbar-toggle"
            aria-label="Toggle Navigation"
            onClick={toggleMobileMenu}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              width="24"
              height="24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              {isMobileMenuOpen ? (
                // X icon when menu is open
                <>
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </>
              ) : (
                // Hamburger icon when menu is closed
                <>
                  <line x1="3" y1="12" x2="21" y2="12"></line>
                  <line x1="3" y1="6" x2="21" y2="6"></line>
                  <line x1="3" y1="18" x2="21" y2="18"></line>
                </>
              )}
            </svg>
          </button>
        </div>
      </nav>

      {/* Conditionally render Login Form */}
      {showLogin && (
        <div className="modal-overlay">
          <div className="modal-content">
             <button onClick={() => setShowLogin(false)} style={{float: 'right'}}>X</button>
             <h2>Login</h2>
             <LoginForm
               onAuthSuccess={(user) => {
                 setIsLoggedIn(true);
                 setUserInfo(user);
                 setShowLogin(false);
               }}
             />
          </div>
        </div>
      )}

      {/* Conditionally render Signup Form */}
      {showSignup && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button onClick={() => setShowSignup(false)} style={{float: 'right'}}>X</button>
            <h2>Sign Up</h2>
            <SignupForm
              onAuthSuccess={(user) => {
                setIsLoggedIn(true);
                setUserInfo(user);
                setShowSignup(false);
              }}
            />
          </div>
        </div>
      )}
    </>
  );
}

export default Header;