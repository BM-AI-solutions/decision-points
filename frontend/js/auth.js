// frontend/js/auth.js

// Initialize the Google Sign-In client
function initGoogleSignIn() {
  google.accounts.id.initialize({
    client_id: 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com', // Replace with your Google Client ID
    callback: handleCredentialResponse  // Callback function handling the sign-in
  });

  // Render the Google Sign-In button
  google.accounts.id.renderButton(
    document.getElementById("google-signin-button-container"), // HTML element where the button will be rendered
    { theme: "outline", size: "large" }  // Optional configuration
  );
}

// Handle the sign-in response
function handleCredentialResponse(response) {
  // Decode the JWT id_token
  const tokenResponse = google.accounts.id.token.parseCredential(response.credential);

  // You can now use the ID token to authenticate with your backend
  console.log("ID Token:", tokenResponse.sub);
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
      // Redirect or update UI accordingly
      window.location.href = '/dashboard'; // Example redirect
    } else {
      console.error("Authentication failed:", data.message);
      alert("Authentication failed. Please try again.");
    }
  })
  .catch(error => {
    console.error("Error:", error);
    alert("An error occurred. Please try again.");
  });
}

// Call initGoogleSignIn when the window loads
window.onload = initGoogleSignIn;
