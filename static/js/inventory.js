// Function to add a new inventory item
async function addInventoryItem(event) {
    event.preventDefault();
  
    const name = document.getElementById('item-name').value;
    const category = document.getElementById('item-category').value;
    const quantity = document.getElementById('item-quantity').value;
    const unit = document.getElementById('item-unit').value;
    const expiryDate = document.getElementById('item-expiry-date').value;
  
    if (!name || !category || !quantity || !unit || !expiryDate) {
      displayError('Please fill out all fields.');
      return;
    }
  
    try {
      const response = await fetch('/inventory/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, category, quantity, unit, expiry_date: expiryDate }),
      });
  
      const result = await response.json();
  
      if (result.success) {
        window.location.reload();
      } else {
        displayError(result.error || 'Failed to add inventory item.');
      }
    } catch (error) {
      console.error('Error adding inventory item:', error);
      displayError('An error occurred. Please try again.');
    }
  }
  
  // Function to update an inventory item
  async function updateInventoryItem(itemId) {
    const name = document.getElementById(`item-name-${itemId}`).value;
    const category = document.getElementById(`item-category-${itemId}`).value;
    const quantity = document.getElementById(`item-quantity-${itemId}`).value;
    const unit = document.getElementById(`item-unit-${itemId}`).value;
    const expiryDate = document.getElementById(`item-expiry-date-${itemId}`).value;
  
    if (!name || !category || !quantity || !unit || !expiryDate) {
      displayError('Please fill out all fields.');
      return;
    }
  
    try {
      const response = await fetch('/inventory/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: itemId, name, category, quantity, unit, expiry_date: expiryDate }),
      });
  
      const result = await response.json();
  
      if (result.success) {
        window.location.reload();
      } else {
        displayError(result.error || 'Failed to update inventory item.');
      }
    } catch (error) {
      console.error('Error updating inventory item:', error);
      displayError('An error occurred. Please try again.');
    }
  }
  
  // Function to delete an inventory item
  async function deleteInventoryItem(itemId) {
    try {
      const response = await fetch('/inventory/delete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: itemId }),
      });
  
      const result = await response.json();
  
      if (result.success) {
        window.location.reload();
      } else {
        displayError(result.error || 'Failed to delete inventory item.');
      }
    } catch (error) {
      console.error('Error deleting inventory item:', error);
      displayError('An error occurred. Please try again.');
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
    const addItemForm = document.getElementById('add-item-form');
    if (addItemForm) {
      addItemForm.addEventListener('submit', addInventoryItem);
    }
  
    const updateButtons = document.querySelectorAll('.update-item-button');
    updateButtons.forEach(button => {
      button.addEventListener('click', () => {
        const itemId = button.dataset.itemId;
        updateInventoryItem(itemId);
      });
    });
  
    const deleteButtons = document.querySelectorAll('.delete-item-button');
    deleteButtons.forEach(button => {
      button.addEventListener('click', () => {
        const itemId = button.dataset.itemId;
        deleteInventoryItem(itemId);
      });
    });
  });