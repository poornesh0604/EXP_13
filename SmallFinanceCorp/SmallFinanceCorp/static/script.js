/**
 * Small Finance Corporation - Main JavaScript Functions
 * Handles interactive features, form validation, and UI enhancements
 */

// Global variables
let currentTheme = 'dark';
let loadingStates = new Map();

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    setupEventListeners();
    initializeTooltips();
    initializeModals();
    setupFormValidation();
    initializeCharts();
    handleNavigation();
    setupSearchFunctionality();
    initializeNotifications();
}

/**
 * Setup global event listeners
 */
function setupEventListeners() {
    // Handle responsive navigation
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            const navbar = document.querySelector('.navbar-collapse');
            navbar.classList.toggle('show');
        });
    }

    // Handle form submissions with loading states
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                showButtonLoading(submitBtn);
            }
        });
    });

    // Handle table row clicks for mobile
    document.querySelectorAll('.table-responsive .table tbody tr').forEach(row => {
        row.addEventListener('click', function(e) {
            if (window.innerWidth <= 768 && !e.target.closest('.btn')) {
                const firstBtn = this.querySelector('.btn');
                if (firstBtn) {
                    firstBtn.click();
                }
            }
        });
    });

    // Handle quick actions
    document.querySelectorAll('[data-action]').forEach(element => {
        element.addEventListener('click', handleQuickAction);
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Bootstrap modals
 */
function initializeModals() {
    // Auto-focus first input in modals
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = this.querySelector('input, select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    // Real-time validation for amount fields
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', function() {
            validateNumberInput(this);
        });

        input.addEventListener('blur', function() {
            formatNumberInput(this);
        });
    });

    // Email validation
    document.querySelectorAll('input[type="email"]').forEach(input => {
        input.addEventListener('blur', function() {
            validateEmailInput(this);
        });
    });

    // Phone number formatting
    document.querySelectorAll('input[name*="phone"]').forEach(input => {
        input.addEventListener('input', function() {
            formatPhoneInput(this);
        });
    });

    // Date validation
    document.querySelectorAll('input[type="date"]').forEach(input => {
        input.addEventListener('change', function() {
            validateDateInput(this);
        });
    });
}

/**
 * Initialize charts if Chart.js is available
 */
function initializeCharts() {
    if (typeof Chart !== 'undefined') {
        // Set global chart defaults
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        Chart.defaults.plugins.legend.display = true;
        Chart.defaults.elements.arc.borderWidth = 2;
        Chart.defaults.elements.line.tension = 0.4;
    }
}

/**
 * Handle navigation highlighting
 */
function handleNavigation() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        }
    });
}

/**
 * Setup search functionality
 */
function setupSearchFunctionality() {
    const searchInputs = document.querySelectorAll('input[name="search"]');
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const form = this.closest('form');
            
            searchTimeout = setTimeout(() => {
                if (this.value.length >= 3 || this.value.length === 0) {
                    // Auto-submit search form after 500ms delay
                    if (form) {
                        form.submit();
                    }
                }
            }, 500);
        });
    });
}

/**
 * Initialize notifications
 */
function initializeNotifications() {
    // Auto-hide alerts after 5 seconds
    document.querySelectorAll('.alert[role="alert"]').forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * Validation Functions
 */

function validateNumberInput(input) {
    const value = parseFloat(input.value);
    const min = input.min ? parseFloat(input.min) : 0;
    const max = input.max ? parseFloat(input.max) : Infinity;

    if (isNaN(value) || value < min || value > max) {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
    } else {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    }
}

function formatNumberInput(input) {
    if (input.value && !isNaN(input.value)) {
        const value = parseFloat(input.value);
        if (input.step && input.step.includes('.')) {
            const decimals = input.step.split('.')[1].length;
            input.value = value.toFixed(decimals);
        } else {
            input.value = Math.round(value);
        }
    }
}

function validateEmailInput(input) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (input.value && !emailRegex.test(input.value)) {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
    } else if (input.value) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    } else {
        input.classList.remove('is-invalid', 'is-valid');
    }
}

function formatPhoneInput(input) {
    let value = input.value.replace(/\D/g, '');
    
    if (value.length >= 10) {
        // Format as (XXX) XXX-XXXX for US format or similar
        if (value.length === 10) {
            value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
        } else {
            value = value.replace(/(\d+)(\d{3})(\d{4})/, '$1-$2-$3');
        }
    }
    
    input.value = value;
}

function validateDateInput(input) {
    const selectedDate = new Date(input.value);
    const today = new Date();
    const maxDate = input.max ? new Date(input.max) : null;
    const minDate = input.min ? new Date(input.min) : null;

    if (selectedDate > today && !input.classList.contains('future-allowed')) {
        input.classList.add('is-invalid');
        showTooltip(input, 'Date cannot be in the future');
    } else if (maxDate && selectedDate > maxDate) {
        input.classList.add('is-invalid');
        showTooltip(input, 'Date exceeds maximum allowed');
    } else if (minDate && selectedDate < minDate) {
        input.classList.add('is-invalid');
        showTooltip(input, 'Date is before minimum allowed');
    } else {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    }
}

/**
 * UI Helper Functions
 */

function showButtonLoading(button) {
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    
    loadingStates.set(button, originalText);
    
    // Auto-restore after 30 seconds as failsafe
    setTimeout(() => {
        hideButtonLoading(button);
    }, 30000);
}

function hideButtonLoading(button) {
    if (loadingStates.has(button)) {
        button.innerHTML = loadingStates.get(button);
        button.disabled = false;
        loadingStates.delete(button);
    }
}

function showTooltip(element, message) {
    const tooltip = new bootstrap.Tooltip(element, {
        title: message,
        trigger: 'manual'
    });
    tooltip.show();
    
    setTimeout(() => {
        tooltip.hide();
        tooltip.dispose();
    }, 3000);
}

function showNotification(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

/**
 * Financial Calculation Functions
 */

function calculateEMI(principal, annualRate, months) {
    const monthlyRate = annualRate / 1200; // Convert to monthly decimal
    
    if (monthlyRate === 0) {
        return principal / months;
    }
    
    const emi = (principal * monthlyRate * Math.pow(1 + monthlyRate, months)) / 
                (Math.pow(1 + monthlyRate, months) - 1);
    
    return Math.round(emi * 100) / 100; // Round to 2 decimal places
}

function calculateTotalInterest(emi, months, principal) {
    return (emi * months) - principal;
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatNumber(number) {
    return new Intl.NumberFormat('en-IN').format(number);
}

/**
 * Data Export Functions
 */

function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = Array.from(table.querySelectorAll('tr'));
    const csvContent = rows.map(row => {
        const cells = Array.from(row.querySelectorAll('th, td'));
        return cells.map(cell => {
            const text = cell.textContent.trim();
            return `"${text.replace(/"/g, '""')}"`;
        }).join(',');
    }).join('\n');
    
    downloadCSV(csvContent, filename);
}

function downloadCSV(content, filename) {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

/**
 * Quick Action Handler
 */

function handleQuickAction(event) {
    const action = event.target.dataset.action;
    const target = event.target.dataset.target;
    
    switch (action) {
        case 'calculate-emi':
            calculateEMIFromForm(target);
            break;
        case 'validate-form':
            validateForm(target);
            break;
        case 'export-data':
            exportTableToCSV(target, 'finance_data.csv');
            break;
        case 'refresh-data':
            window.location.reload();
            break;
        default:
            console.warn('Unknown action:', action);
    }
}

/**
 * Form-specific Functions
 */

function calculateEMIFromForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const principal = parseFloat(form.querySelector('[name*="amount"]')?.value || 0);
    const rate = parseFloat(form.querySelector('[name*="rate"]')?.value || 0);
    const months = parseInt(form.querySelector('[name*="duration"]')?.value || 0);
    
    if (principal && rate && months) {
        const emi = calculateEMI(principal, rate, months);
        const totalPayable = emi * months;
        const totalInterest = totalPayable - principal;
        
        // Display results
        const resultContainer = form.querySelector('.emi-result');
        if (resultContainer) {
            resultContainer.innerHTML = `
                <div class="row text-center">
                    <div class="col-md-4">
                        <h6 class="text-success">Monthly EMI</h6>
                        <h4>${formatCurrency(emi)}</h4>
                    </div>
                    <div class="col-md-4">
                        <h6 class="text-info">Total Payable</h6>
                        <h4>${formatCurrency(totalPayable)}</h4>
                    </div>
                    <div class="col-md-4">
                        <h6 class="text-warning">Total Interest</h6>
                        <h4>${formatCurrency(totalInterest)}</h4>
                    </div>
                </div>
            `;
        }
    }
}

function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    let isValid = true;
    
    // Validate required fields
    form.querySelectorAll('[required]').forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    // Validate number fields
    form.querySelectorAll('input[type="number"]').forEach(field => {
        validateNumberInput(field);
        if (field.classList.contains('is-invalid')) {
            isValid = false;
        }
    });
    
    // Validate email fields
    form.querySelectorAll('input[type="email"]').forEach(field => {
        validateEmailInput(field);
        if (field.classList.contains('is-invalid')) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Utility Functions
 */

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Mobile-specific enhancements
if (window.innerWidth <= 768) {
    // Add touch-friendly classes
    document.body.classList.add('mobile-device');
    
    // Enhance table interactions for mobile
    document.querySelectorAll('.table-responsive').forEach(container => {
        container.addEventListener('scroll', throttle(() => {
            // Show scroll indicator
            container.classList.add('scrolling');
            setTimeout(() => {
                container.classList.remove('scrolling');
            }, 1000);
        }, 100));
    });
}

// Performance monitoring
if (typeof PerformanceObserver !== 'undefined') {
    const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
            if (entry.loadTime > 1000) {
                console.warn('Slow loading component:', entry.name, entry.loadTime + 'ms');
            }
        }
    });
    
    observer.observe({ entryTypes: ['measure'] });
}

// Error handling
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    showNotification('An error occurred. Please refresh the page and try again.', 'danger');
});

// Expose global functions for template use
window.FinanceApp = {
    calculateEMI,
    formatCurrency,
    formatNumber,
    showNotification,
    exportTableToCSV,
    validateForm
};
