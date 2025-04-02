// Function to handle login
async function handleLogin(event) {
    event.preventDefault();
  
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
  
    if (!username || !password) {
      displayError('Please enter both username and password.');
      return;
    }
  
    try {
      const response = await fetch('/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });
  
      const result = await response.json();
  
      if (result.success) {
        window.location.href = '/dashboard';
      } else {
        displayError(result.error || 'Invalid login credentials.');
      }
    } catch (error) {
      console.error('Error during login:', error);
      displayError('An error occurred. Please try again.');
    }
  }
  
  // Function to handle logout
  async function handleLogout() {
    try {
      const response = await fetch('/logout', {
        method: 'POST',
      });
  
      if (response.ok) {
        window.location.href = '/login';
      } else {
        console.error('Logout failed.');
      }
    } catch (error) {
      console.error('Error during logout:', error);
    }
  }
  
  // Function to display error messages
  function displayError(message) {
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
      errorElement.textContent = message;
      errorElement.style.display = 'block';
    }
  }
  
  // Attach event listeners
  document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
      loginForm.addEventListener('submit', handleLogin);
    }
  
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
      logoutButton.addEventListener('click', handleLogout);
    }
  });