// Function to handle navigation between views
function navigateTo(view) {
    window.location.href = `/${view}`;
  }
  
  // Function to display alerts
  function showAlert(message, type = 'info') {
    const alertBox = document.getElementById('alert-box');
    if (alertBox) {
      alertBox.textContent = message;
      alertBox.className = `alert alert-${type}`;
      alertBox.style.display = 'block';
  
      // Automatically hide the alert after 5 seconds
      setTimeout(() => {
        alertBox.style.display = 'none';
      }, 5000);
    }
  }
  
  // Function to confirm actions (e.g., delete)
  function confirmAction(message, callback) {
    if (confirm(message)) {
      callback();
    }
  }
  
  // Function to toggle visibility of elements
  function toggleVisibility(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
      element.style.display = element.style.display === 'none' ? 'block' : 'none';
    }
  }
  
  // Function to handle form submissions
  async function handleFormSubmit(event, endpoint, successCallback) {
    event.preventDefault();
  
    const form = event.target;
    const formData = new FormData(form);
  
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });
  
      const result = await response.json();
  
      if (result.success) {
        successCallback();
      } else {
        showAlert(result.error || 'An error occurred.', 'danger');
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      showAlert('An error occurred. Please try again.', 'danger');
    }
  }
  
  // Attach event listeners
  document.addEventListener('DOMContentLoaded', () => {
    // Example: Attach navigation buttons
    const navButtons = document.querySelectorAll('.nav-button');
    navButtons.forEach(button => {
      button.addEventListener('click', () => {
        const view = button.dataset.view;
        navigateTo(view);
      });
    });
  
    // Example: Attach form submission handlers
    const forms = document.querySelectorAll('.ajax-form');
    forms.forEach(form => {
      form.addEventListener('submit', event => {
        const endpoint = form.dataset.endpoint;
        handleFormSubmit(event, endpoint, () => {
          showAlert('Action completed successfully!', 'success');
          window.location.reload();
        });
      });
    });
  });