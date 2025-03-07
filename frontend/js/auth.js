// frontend/js/auth.js

// Initialize the Google Sign-In client
function initGoogleSignIn() {
  // Check if Google Sign-In API is loaded
  if (typeof google !== 'undefined' && google.accounts) {
    google.accounts.id.initialize({
      client_id: '706670564943-pmitiums8ciksifmpmio5v5dtcius8rd.apps.googleusercontent.com', // Production Google Client ID
      callback: handleCredentialResponse, // Callback function handling the sign-in
      auto_select: false, // Don't auto-select any account
      cancel_on_tap_outside: true // Allow canceling by tapping outside
    });

    // Render the Google Sign-In button
    const buttonContainer = document.getElementById("google-signin-button-container");
    if (buttonContainer) {
      // Clear any existing content
      buttonContainer.innerHTML = '';
      
      google.accounts.id.renderButton(
        buttonContainer, // HTML element where the button will be rendered
        { 
          type: "standard", // Use standard button type
          theme: "outline", // Use outline theme for dark backgrounds
          size: "large", // Large button size
          text: "signin_with",
          shape: "rectangular",
          width: buttonContainer.clientWidth // Make button width match container
        }
      );
      
      // Make the container visible and properly sized
      buttonContainer.style.display = 'flex';
      buttonContainer.style.justifyContent = 'center';
      buttonContainer.style.alignItems = 'center';
      buttonContainer.style.width = '100%';
      buttonContainer.style.minHeight = '40px';
    } else {
      console.error("Google Sign-In button container not found");
    }
  } else {
    console.error("Google Sign-In API not loaded");
    // Load the Google Sign-In API
    loadGoogleAPI();
  }
}

// Function to load the Google Sign-In API
function loadGoogleAPI() {
  // Check if the script is already loaded to prevent duplicates
  if (document.querySelector('script[src="https://accounts.google.com/gsi/client"]')) {
    console.log("Google Sign-In API script already exists, initializing...");
    setTimeout(initGoogleSignIn, 100); // Give it a moment to initialize
    return;
  }
  
  const script = document.createElement('script');
  script.src = 'https://accounts.google.com/gsi/client';
  script.async = true;
  script.defer = true;
  script.onload = initGoogleSignIn;
  script.onerror = () => console.error("Failed to load Google Sign-In API");
  document.body.appendChild(script);
}

// Handle the sign-in response
function handleCredentialResponse(response) {
  try {
    if (response && response.credential) {
      // Use the ID token to authenticate with your backend
      console.log("ID Token received:", response.credential.substring(0, 10) + "...");
      
      // For demo purposes, simulate a successful auth without backend
      // In production, you would send the token to your backend
      console.log("Authentication successful");
      // Show success message
      showAuthSuccess();
      // Redirect after a short delay
      setTimeout(() => {
        // For demo, just simulate a redirect
        alert("Redirecting to dashboard... (simulated for demo)");
        // window.location.href = '/dashboard'; // Uncomment in production
      }, 1500);
      
      /* Production code (uncomment when backend is ready)
      fetch('/auth/google', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id_token: response.credential })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          console.log("Authentication successful");
          showAuthSuccess();
          setTimeout(() => {
            window.location.href = '/dashboard';
          }, 1500);
        } else {
          console.error("Authentication failed:", data.message);
          alert("Authentication failed. Please try again.");
        }
      })
      .catch(error => {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
      });
      */
    } else {
      console.error("No credential received");
    }
  } catch (error) {
    console.error("Error handling credential response:", error);
  }
}

// Show authentication success message
function showAuthSuccess() {
  const modal = document.getElementById('login-modal');
  if (modal) {
    const modalBody = modal.querySelector('.modal-body');
    modalBody.innerHTML = `
      <div class="auth-success">
        <i class="fas fa-check-circle auth-success-icon"></i>
        <h4>Login Successful!</h4>
        <p>Redirecting to your dashboard...</p>
      </div>
    `;
  }
}

// Function to prompt one-tap sign in
function promptOneTap() {
  if (typeof google !== 'undefined' && google.accounts) {
    google.accounts.id.prompt();
  }
}

// Initialize when the document is fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Try to load Google Sign-In API
  loadGoogleAPI();
  
  // Also initialize when the login modal is shown
  const loginModal = document.getElementById('login-modal');
  if (loginModal) {
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.attributeName === 'style' && 
            loginModal.style.display === 'flex') {
          // Modal is visible, initialize Google Sign-In
          loadGoogleAPI();
        }
      });
    });
    
    observer.observe(loginModal, { attributes: true });
  }
});
