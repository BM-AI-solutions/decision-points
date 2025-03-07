// frontend/js/auth.js

// Initialize the Google Sign-In client
function initGoogleSignIn() {
  // Check if Google Sign-In API is loaded
  if (typeof google !== 'undefined' && google.accounts) {
    google.accounts.id.initialize({
      client_id: '706670564943-pmitiums8ciksifmpmio5v5dtcius8rd.apps.googleusercontent.com', // Production Google Client ID
      callback: handleCredentialResponse // Callback function handling the sign-in
    });

    // Render the Google Sign-In button
    const buttonContainer = document.getElementById("google-signin-button-container");
    if (buttonContainer) {
      google.accounts.id.renderButton(
        buttonContainer, // HTML element where the button will be rendered
        { 
          type: "standard", // Use standard button type
          theme: "outline", // Use outline theme for dark backgrounds
          size: "large", // Large button size
          text: "signin_with",
          shape: "rectangular",
          width: buttonContainer.offsetWidth // Make button width match container
        }
      );
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
  const script = document.createElement('script');
  script.src = 'https://accounts.google.com/gsi/client';
  script.async = true;
  script.defer = true;
  script.onload = initGoogleSignIn;
  document.body.appendChild(script);
}

// Handle the sign-in response
function handleCredentialResponse(response) {
  try {
    if (response.credential) {
      // Use the ID token to authenticate with your backend
      console.log("ID Token received:", response.credential.substring(0, 10) + "...");
      
      // Send the ID token to your backend for validation and session creation
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
          // Show success message
          showAuthSuccess();
          // Redirect after a short delay
          setTimeout(() => {
            window.location.href = '/dashboard'; // Example redirect
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

// Initialize when the document is fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Try to load Google Sign-In API
  loadGoogleAPI();
});
