/**
 * Charts Visualization Logic
 * Responsible for rendering the dynamic progress bars on the dashboard.
 * - Reads financial data embedded in the DOM from Flask
 * - Calculates percentage of income spent per category
 * - Updates the width and color of progress bars
 */
document.addEventListener('DOMContentLoaded', function() {
    
    // Retrieve the data container element
    const dataDisplay = document.getElementById('financial-data');
    if (!dataDisplay) return;

    // Parse financial totals from data attributes (stored by Flask template)
    const totalIncome = parseFloat(dataDisplay.getAttribute('data-total-income')) || 0;
    const totalFixed = parseFloat(dataDisplay.getAttribute('data-total-fixed')) || 0;
    const totalFun = parseFloat(dataDisplay.getAttribute('data-total-fun')) || 0;
    const totalFuture = parseFloat(dataDisplay.getAttribute('data-total-future')) || 0;

    // Define target percentages for the 50/30/20 rule
    const TARGET_FIXED = 50;
    const TARGET_FUN = 30;
    const TARGET_FUTURE = 20;

    /**
     * Updates a single chart bar and its associated label.
     * 
     * @param {number} totalAmount - The total spent/saved in this category
     * @param {number} targetPercent - The goal percentage (e.g., 50)
     * @param {string} barClass - The CSS class of the bar to update (e.g., 'bar-fixed')
     * @param {string} labelClass - The CSS class of the label to update (e.g., 'percent-fixed')
     */
    function updateChart(totalAmount, targetPercent, barClass, labelClass) {
        let percent = 0;
        
        // Calculate percentage of total income
        if (totalIncome > 0) {
            percent = (totalAmount / totalIncome) * 100;
        }

        // Update the percentage text label
        const label = document.querySelector(`.${labelClass}`);
        if(label) {
            // Display decimal only if not a whole number to keep it clean, or 1 decimal fixed if needed
            label.textContent = (percent % 1 === 0 ? percent : percent.toFixed(1)) + '%';
        }

        // Update the visual bar
        const bar = document.querySelector(`.${barClass}`);
        if (bar) {
            // Cap visual width at 100% to prevent overflow, but the logic above uses real percent
            bar.style.width = `${Math.min(percent, 100)}%`;
            
            // Check against target line to change color if over budget
            const targetLine = bar.parentElement.querySelector('.target-line');
            if (targetLine) {
                if (percent > targetPercent) {
                    // Turn RED if over budget
                    targetLine.style.backgroundColor = 'red';
                    bar.style.backgroundColor = 'red';
                } else {
                    // Reset to default colors (defined in CSS) if within budget
                    targetLine.style.backgroundColor = ''; 
                    bar.style.backgroundColor = '';
                }
            }
        }
    }

    // Initialize charts for all three categories
    updateChart(totalFixed, TARGET_FIXED, 'bar-fixed', 'percent-fixed');
    updateChart(totalFun, TARGET_FUN, 'bar-fun', 'percent-fun');
    updateChart(totalFuture, TARGET_FUTURE, 'bar-future', 'percent-future');
});
