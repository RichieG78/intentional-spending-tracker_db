/**
 * Dashboard Interaction Logic
 * Handles client-side interactivity for the financial dashboard, including:
 * - Deleting expenses and income
 * - Inline editing of descriptions and amounts
 * - Sending AJAX requests to the Flask backend to update data without full page reloads
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // --- Expense Handlers ---

    /**
     * DELETE EXPENSE
     * Attaches click event listeners to all 'Delete' buttons on expense cards.
     * asks for confirmation before sending a DELETE request to the server.
     */
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', function() {
            // Find the parent card element to get the ID
            const card = this.closest('.transaction-card');
            const expenseId = card.dataset.id;
            
            if(confirm('Are you sure you want to delete this expense?')) {
                // Send DELETE request to Flask backend
                fetch(`/delete-expense/${expenseId}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Remove the element from the DOM immediately
                        card.remove();
                        // Reload data to recalculate totals and update charts
                        location.reload(); 
                    } else {
                        alert('Error deleting expense');
                    }
                });
            }
        });
    });

    /**
     * EDIT EXPENSE
     * Handles the 'Edit' / 'Save' toggle functionality for expenses.
     * - First click: Converts text fields to input fields (Edit Mode)
     * - Second click: Sends updated data to server and converts back to text (Save Mode)
     */
    document.querySelectorAll('.btn-edit').forEach(button => {
        button.addEventListener('click', function() {
            const card = this.closest('.transaction-card');
            const expenseId = card.dataset.id;
            
            // Get references to current DOM elements
            const detailsDiv = card.querySelector('.transaction-details');
            const titleEl = detailsDiv.querySelector('.transaction-title');
            const amountEl = detailsDiv.querySelector('.transaction-amount');
            
            // CHECK MODE: If button says 'Save', we are currently in Edit Mode -> Submit changes
            if (this.textContent === 'Save') {
                // Extract values from the inputs
                const newDesc = titleEl.querySelector('input').value;
                const newAmount = amountEl.querySelector('input').value;

                // Send POST request (UPDATE) to Flask backend
                fetch(`/update-expense/${expenseId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        description: newDesc,
                        amount: newAmount
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update UI with new static values
                        titleEl.textContent = newDesc;
                        amountEl.textContent = '$' + parseFloat(newAmount).toFixed(2);
                        this.textContent = 'Edit'; // Reset button text
                         location.reload(); // Refresh to update charts/totals
                    } else {
                        alert('Error updating expense');
                    }
                });

            } else {
                // ENTER EDIT MODE: Replace text with input fields
                const currentTitle = titleEl.textContent;
                const currentAmount = amountEl.textContent.replace('$', '').trim();

                // Inject HTML input fields
                titleEl.innerHTML = `<input type="text" value="${currentTitle}" class="edit-input-title">`;
                amountEl.innerHTML = `<input type="number" step="0.01" value="${currentAmount}" class="edit-input-amount">`;
                
                this.textContent = 'Save'; // Change button text
            }
        });
    });

    // --- Income Handlers ---
    
    /**
     * DELETE INCOME
     * Similar to expense deletion but targets income rows.
     */
    document.querySelectorAll('.btn-delete-income').forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('.income-row');
            const incomeId = row.dataset.id;
            
            if (!incomeId) return; 

            if(confirm('Are you sure you want to delete this income source?')) {
                fetch(`/delete-income/${incomeId}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        row.remove();
                        location.reload(); 
                    } else {
                        alert('Error deleting income');
                    }
                });
            }
        });
    });

    /**
     * EDIT INCOME
     * Handles inline editing for income sources.
     * Toggles between text display and input fields.
     */
    document.querySelectorAll('.btn-edit-income').forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('.income-row');
            const incomeId = row.dataset.id;
            if (!incomeId) return;

            const detailsWrapper = row.querySelector('.income-details-wrapper');
            const titleEl = detailsWrapper.querySelector('.income-title');
            const amountEl = detailsWrapper.querySelector('.income-amount');
            
            // SAVE CHANGES
            if (this.textContent === 'Save') {
                const newDesc = titleEl.querySelector('input').value;
                const newAmount = amountEl.querySelector('input').value;

                fetch(`/update-income/${incomeId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        description: newDesc,
                        amount: newAmount
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        titleEl.textContent = newDesc;
                        amountEl.textContent = '$' + parseFloat(newAmount).toFixed(2);
                        this.textContent = 'Edit';
                        location.reload();
                    } else {
                        alert('Error updating income');
                    }
                });

            } else {
                // ENTER EDIT MODE
                const currentTitle = titleEl.textContent;
                const currentAmount = amountEl.textContent.replace('$', '').trim();

                titleEl.innerHTML = `<input type="text" value="${currentTitle}" class="edit-income-title">`;
                amountEl.innerHTML = `<input type="number" step="0.01" value="${currentAmount}" class="edit-income-amount">`;
                
                this.textContent = 'Save';
            }
        });
    });

});
