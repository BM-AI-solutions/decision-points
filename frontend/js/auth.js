/**
 * Authentication module for the Dual Agent System
 * 
 * Handles OAuth authentication with Google and GitHub,
 * and user session management.
 */

class AuthService {
  constructor() {
    this.currentUser = null;
    this.authListeners = [];
    
    // Initialize auth state
    this.checkAuthState();
    
    // Set up Google OAuth
    this.loadGoogleAuth();
    
    // Add event listeners to auth buttons
    this.setupEventListeners();
  }
  
  /**
   * Load Google OAuth API
   */
  loadGoogleAuth() {
    // Load Google's API script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
    
    // Initialize Google auth when script is loaded
    script.onload = () => {
      if (window.google) {
        google.accounts.id.initialize({
          client_id: '116937668968-g0d3oevk2uh6ikng4igu18l4jjq6puhs.apps.googleusercontent.com', // Example client ID - replace with your actual Google OAuth client ID
          callback: this.handleGoogleResponse.bind(this),
          auto_select: false
        });
      }
    };
  }
  
  /**
   * Handle response from Google OAuth
   */
  async handleGoogleResponse(response) {
    try {
      // Send the ID token to backend
      const result = await apiService.loginWithGoogle({
        token: response.credential
      });
      
      this.setCurrentUser(result.user);
      this.notifyAuthChange(true);
      
      // Show success notification
      this.showNotification('Successfully signed in with Google', 'success');
      
      // Close any open modals
      this.closeAllModals();
      
      // Redirect to dashboard or refresh
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 1000);
    } catch (error) {
      console.error('Google auth error:', error);
      this.showNotification('Failed to authenticate with Google', 'error');
    }
  }
  
  /**
   * Handle GitHub authentication
   */
  async authenticateWithGithub() {
    // GitHub OAuth redirect URL
    const clientId = 'your-github-client-id'; // Replace with your GitHub client ID
    const redirectUri = encodeURIComponent(window.location.origin + '/auth/github/callback');
    const scope = encodeURIComponent('user:email');
    
    // Store the current URL in session storage to redirect back after auth
    sessionStorage.setItem('auth_redirect', window.location.href);
    
    // Redirect to GitHub OAuth page
    window.location.href = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}`;
  }
  
  /**
   * Handle login with email and password
   */
  async login(email, password) {
    try {
      const result = await apiService.login(email, password);
      this.setCurrentUser(result.user);
      this.notifyAuthChange(true);
      return result;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }
  
  /**
   * Handle user registration
   */
  async signup(userData) {
    try {
      const result = await apiService.signup(userData);
      this.setCurrentUser(result.user);
      this.notifyAuthChange(true);
      return result;
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  }
  
  /**
   * Log out the current user
   */
  async logout() {
    try {
      await apiService.logout();
      this.setCurrentUser(null);
      this.notifyAuthChange(false);
      
      // Show logout notification
      this.showNotification('You have been logged out', 'info');
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
  
  /**
   * Check the current authentication state
   */
  async checkAuthState() {
    try {
      const user = await apiService.getCurrentUser();
      this.setCurrentUser(user);
      this.notifyAuthChange(true);
      return user;
    } catch (error) {
      // User is not authenticated - this is expected behavior
      this.setCurrentUser(null);
      this.notifyAuthChange(false);
      return null;
    }
  }
  
  /**
   * Set the current user
   */
  setCurrentUser(user) {
    this.currentUser = user;
    
    // Update UI based on auth state
    this.updateUIForAuthState();
  }
  
  /**
   * Update UI elements based on authentication state
   */
  updateUIForAuthState() {
    const isLoggedIn = !!this.currentUser;
    
    // Update login/signup buttons
    const authButtons = document.querySelector('.auth-buttons');
    if (authButtons) {
      if (isLoggedIn) {
        authButtons.innerHTML = `
          <button class="btn btn-primary">Dashboard</button>
          <button class="btn btn-logout">Logout</button>
        `;
        
        // Add event listeners to the new buttons
        const dashboardBtn = authButtons.querySelector('.btn-primary');
        const logoutBtn = authButtons.querySelector('.btn-logout');
        
        if (dashboardBtn) {
          dashboardBtn.addEventListener('click', () => {
            window.location.href = '/dashboard';
          });
        }
        
        if (logoutBtn) {
          logoutBtn.addEventListener('click', () => {
            this.logout();
          });
        }
      } else {
        authButtons.innerHTML = `
          <button class="btn btn-login">Login</button>
          <button class="btn btn-primary">Sign Up</button>
        `;
        
        // Reinitialize event listeners
        this.setupEventListeners();
      }
    }
  }
  
  /**
   * Register an auth state change listener
   */
  onAuthStateChanged(callback) {
    this.authListeners.push(callback);
    
    // Immediately call with current state
    callback(!!this.currentUser, this.currentUser);
    
    // Return an unsubscribe function
    return () => {
      this.authListeners = this.authListeners.filter(cb => cb !== callback);
    };
  }
  
  /**
   * Notify all listeners of auth state change
   */
  notifyAuthChange(isLoggedIn) {
    this.authListeners.forEach(callback => {
      callback(isLoggedIn, this.currentUser);
    });
  }
  
  /**
   * Set up event listeners for auth-related buttons
   */
  setupEventListeners() {
    // Login button
    const loginBtn = document.querySelector('.btn-login');
    if (loginBtn) {
      loginBtn.addEventListener('click', () => {
        this.openLoginModal();
      });
    }
    
    // Sign up button
    const signUpBtn = document.querySelector('.btn-primary');
    if (signUpBtn && signUpBtn.closest('.auth-buttons')) {
      signUpBtn.addEventListener('click', () => {
        this.openSignupModal();
      });
    }
    
    // Add event listeners to Google and GitHub buttons
    document.querySelectorAll('.btn-google').forEach(button => {
      button.addEventListener('click', () => {
        if (window.google && google.accounts && google.accounts.id) {
          google.accounts.id.prompt();
        } else {
          this.showNotification('Google authentication is initializing, please try again in a moment', 'info');
        }
      });
    });
    
    document.querySelectorAll('.btn-github').forEach(button => {
      button.addEventListener('click', () => {
        this.authenticateWithGithub();
      });
    });
    
    // Login form submission
    const loginForm = document.querySelector('#login-modal .auth-form');
    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        if (!email || !password) {
          this.showNotification('Please enter both email and password', 'error');
          return;
        }
        
        try {
          await this.login(email, password);
          this.closeAllModals();
          this.showNotification('Login successful!', 'success');
          
          // Redirect to dashboard or refresh the page
          setTimeout(() => {
            window.location.href = '/dashboard';
          }, 1000);
        } catch (error) {
          this.showNotification('Login failed: ' + (error.data?.message || 'Invalid credentials'), 'error');
        }
      });
    }
    
    // Signup form submission
    const signupForm = document.querySelector('#app-modal .auth-form');
    if (signupForm) {
      signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('signup-name')?.value;
        const email = document.getElementById('signup-email')?.value;
        const password = document.getElementById('signup-password')?.value;
        const confirm = document.getElementById('signup-confirm')?.value;
        
        // Validate
        if (!name || !email || !password || !confirm) {
          this.showNotification('Please fill out all fields', 'error');
          return;
        }
        
        if (password !== confirm) {
          this.showNotification('Passwords do not match', 'error');
          return;
        }
        
        try {
          await this.signup({ name, email, password });
          
          // Update modal content for success
          const modalBody = document.querySelector('#app-modal .modal-body');
          if (modalBody) {
            modalBody.innerHTML = `
              <div class="success-message">
                <i class="fas fa-check-circle" style="font-size: 3rem; color: var(--success); margin-bottom: 1rem;"></i>
                <h3>Account Created!</h3>
                <p>Welcome to Decision Points AI, ${name}! You can now access your dashboard.</p>
                <button class="btn btn-primary btn-full" id="goto-dashboard">Go to Dashboard</button>
              </div>
            `;
            
            // Add event listener to the dashboard button
            document.getElementById('goto-dashboard')?.addEventListener('click', () => {
              window.location.href = '/dashboard';
            });
          }
        } catch (error) {
          this.showNotification('Signup failed: ' + (error.data?.message || 'Please try again'), 'error');
        }
      });
    }
  }
  
  /**
   * Open the login modal
   */
  openLoginModal() {
    const loginModal = document.getElementById('login-modal');
    if (loginModal) {
      loginModal.style.display = 'flex';
      document.body.style.overflow = 'hidden';
    }
  }
  
  /**
   * Open the signup modal
   */
  openSignupModal() {
    const appModal = document.getElementById('app-modal');
    if (appModal) {
      // Set content for sign up
      const modalBody = appModal.querySelector('.modal-body');
      if (modalBody) {
        modalBody.innerHTML = `
          <form class="auth-form">
            <div class="input-group">
              <label for="signup-name">Full Name</label>
              <input type="text" id="signup-name" class="form-input" placeholder="Your name">
            </div>
            <div class="input-group">
              <label for="signup-email">Email</label>
              <input type="email" id="signup-email" class="form-input" placeholder="your@email.com">
            </div>
            <div class="input-group">
              <label for="signup-password">Password</label>
              <input type="password" id="signup-password" class="form-input" placeholder="••••••••••">
            </div>
            <div class="input-group">
              <label for="signup-confirm">Confirm Password</label>
              <input type="password" id="signup-confirm" class="form-input" placeholder="••••••••••">
            </div>
            <button type="submit" class="btn btn-primary btn-full">Create Account</button>
            <div class="auth-divider">
              <span>or continue with</span>
            </div>
            <div class="social-login">
              <button type="button" class="btn btn-social btn-google">
                <i class="fab fa-google"></i> Google
              </button>
              <button type="button" class="btn btn-social btn-github">
                <i class="fab fa-github"></i> GitHub
              </button>
            </div>
          </form>
        `;
      }
      
      // Set header title
      const modalHeader = appModal.querySelector('.modal-header h3');
      if (modalHeader) {
        modalHeader.textContent = 'Sign Up for Decision Points AI';
      }
      
      // Display the modal
      appModal.style.display = 'flex';
      document.body.style.overflow = 'hidden';
      
      // Add event listeners to the new form
      this.setupEventListeners();
    }
  }
  
  /**
   * Close all modals
   */
  closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
      modal.style.display = 'none';
    });
    document.body.style.overflow = '';
  }
  
  /**
   * Show a notification to the user
   */
  showNotification(message, type = 'info') {
    // Create notification element if it doesn't exist
    let notification = document.querySelector('.notification');
    if (!notification) {
      notification = document.createElement('div');
      notification.className = 'notification';
      document.body.appendChild(notification);
    }
    
    // Set notification content based on type
    let icon;
    let backgroundColor;
    
    switch (type) {
      case 'success':
        icon = 'fa-check-circle';
        backgroundColor = 'var(--success)';
        break;
      case 'error':
        icon = 'fa-exclamation-circle';
        backgroundColor = 'var(--danger)';
        break;
      case 'warning':
        icon = 'fa-exclamation-triangle';
        backgroundColor = 'var(--warning)';
        break;
      case 'info':
      default:
        icon = 'fa-info-circle';
        backgroundColor = 'var(--primary)';
        break;
    }
    
    notification.innerHTML = `
      <div class="notification-content">
        <i class="fas ${icon}"></i> ${message}
      </div>
    `;
    
    // Style the notification
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.backgroundColor = backgroundColor;
    notification.style.color = 'white';
    notification.style.padding = '12px 20px';
    notification.style.borderRadius = 'var(--radius-md)';
    notification.style.boxShadow = 'var(--shadow-md)';
    notification.style.zIndex = '2000';
    notification.style.display = 'flex';
    notification.style.alignItems = 'center';
    notification.style.gap = '10px';
    notification.style.animation = 'slideIn 0.3s ease';
    
    // Add animation if not already added
    if (!document.getElementById('notification-animations')) {
      const styleSheet = document.createElement("style");
      styleSheet.id = 'notification-animations';
      styleSheet.textContent = `
        @keyframes slideIn {
          0% { transform: translateX(100%); opacity: 0; }
          100% { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
          0% { transform: translateX(0); opacity: 1; }
          100% { transform: translateX(100%); opacity: 0; }
        }
      `;
      document.head.appendChild(styleSheet);
    }
    
    // Remove after 3 seconds
    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease';
      notification.addEventListener('animationend', function() {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      });
    }, 3000);
  }
}

// Initialize auth service
const authService = new AuthService();

// Add API methods for OAuth authentication
Object.assign(apiService, {
  loginWithGoogle: (data) => {
    return api.post('/auth/google', data);
  },
  
  loginWithGithub: (data) => {
    return api.post('/auth/github', data);
  }
});

// Export auth service
window.authService = authService;
