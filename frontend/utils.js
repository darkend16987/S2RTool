// ============================================
// SHARED UTILITIES - S2RTool
// Common functions used across all pages
// Version: 1.0
// ============================================

// ============== LOGGING ==============
const IS_PRODUCTION = window.location.hostname !== 'localhost' && !window.location.hostname.includes('127.0.0.1');

function log(...args) {
    if (!IS_PRODUCTION) {
        console.log(...args);
    }
}

function logError(...args) {
    console.error(...args); // Always log errors
}

function logWarn(...args) {
    if (!IS_PRODUCTION) {
        console.warn(...args);
    }
}

// ============== UI HELPERS ==============

/**
 * Show error message in a container
 * @param {string} containerId - ID of the error container
 * @param {string} message - Error message to display
 */
function showError(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
        container.textContent = message;
        container.classList.remove('hidden');
        container.classList.add('visible');
    }
}

/**
 * Show success message in a container
 * @param {string} containerId - ID of the success container
 * @param {string} message - Success message to display
 */
function showSuccess(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
        container.textContent = message;
        container.classList.remove('hidden');
        container.classList.add('visible');
    }
}

/**
 * Hide message container
 * @param {string} containerId - ID of the container to hide
 */
function hideMessage(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.classList.add('hidden');
        container.classList.remove('visible');
    }
}

/**
 * Show or hide spinner
 * @param {string} spinnerId - ID of the spinner element
 * @param {boolean} show - Whether to show or hide
 */
function showSpinner(spinnerId, show) {
    const spinner = document.getElementById(spinnerId);
    if (spinner) {
        if (show) {
            spinner.classList.remove('hidden');
        } else {
            spinner.classList.add('hidden');
        }
    }
}

// ============== IMAGE PROCESSING ==============

/**
 * Optimize image for upload by resizing if needed
 * @param {File} file - The image file to optimize
 * @param {number} maxDimension - Maximum width/height (default 1024)
 * @returns {Promise<Blob>} - Optimized image blob
 */
async function optimizeImageForUpload(file, maxDimension = 1024) {
    return new Promise((resolve, reject) => {
        const img = new Image();

        img.onload = () => {
            const canvas = document.createElement('canvas');
            let { width, height } = img;

            // Calculate new dimensions if image is larger than max
            if (width > maxDimension || height > maxDimension) {
                const ratio = Math.min(maxDimension / width, maxDimension / height);
                width = Math.round(width * ratio);
                height = Math.round(height * ratio);

                log(`📐 Resizing image: ${img.width}×${img.height} → ${width}×${height}`);
            } else {
                log(`📐 Image already optimal: ${width}×${height}`);
            }

            canvas.width = width;
            canvas.height = height;

            const ctx = canvas.getContext('2d');
            ctx.imageSmoothingEnabled = true;
            ctx.imageSmoothingQuality = 'high';

            // Draw resized image
            ctx.drawImage(img, 0, 0, width, height);

            // Convert to blob (PNG lossless)
            canvas.toBlob(resolve, 'image/png');
        };

        img.onerror = () => {
            reject(new Error('Failed to load image'));
        };

        img.src = URL.createObjectURL(file);
    });
}

/**
 * Convert file to base64 string
 * @param {File|Blob} file - File to convert
 * @returns {Promise<string>} - Base64 data URL
 */
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// ============== API HELPERS ==============

/**
 * Make API request with error handling
 * @param {string} url - API endpoint URL
 * @param {object} options - Fetch options
 * @returns {Promise<object>} - Response data
 */
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }

        return data;
    } catch (error) {
        logError('API request failed:', error);
        throw error;
    }
}

// ============== VALIDATION ==============

/**
 * Check if value is not empty
 * @param {any} value - Value to check
 * @returns {boolean}
 */
function isNotEmpty(value) {
    return value !== null && value !== undefined && value !== '';
}

/**
 * Check if file is valid image
 * @param {File} file - File to validate
 * @returns {boolean}
 */
function isValidImage(file) {
    if (!file) return false;
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    return validTypes.includes(file.type);
}

/**
 * Check if file size is within limit
 * @param {File} file - File to check
 * @param {number} maxSizeMB - Maximum size in MB (default 16)
 * @returns {boolean}
 */
function isFileSizeValid(file, maxSizeMB = 16) {
    if (!file) return false;
    const maxBytes = maxSizeMB * 1024 * 1024;
    return file.size <= maxBytes;
}

// ============== DOM HELPERS ==============

/**
 * Safely set innerHTML with null check
 * @param {string} elementId - Element ID
 * @param {string} html - HTML content
 * @returns {boolean} - Whether operation succeeded
 */
function safeSetInnerHTML(elementId, html) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = html;
        return true;
    }
    logWarn(`Element not found: ${elementId}`);
    return false;
}

/**
 * Safely set value with null check
 * @param {string} elementId - Element ID
 * @param {string} value - Value to set
 * @returns {boolean} - Whether operation succeeded
 */
function safeSetValue(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.value = value || '';
        return true;
    }
    logWarn(`Element not found: ${elementId}`);
    return false;
}

/**
 * Safely get element value
 * @param {string} elementId - Element ID
 * @param {string} defaultValue - Default value if element not found
 * @returns {string} - Element value or default
 */
function safeGetValue(elementId, defaultValue = '') {
    const element = document.getElementById(elementId);
    return element ? element.value : defaultValue;
}

// ============== DOWNLOAD HELPERS ==============

/**
 * Download base64 image
 * @param {string} base64Data - Base64 image data
 * @param {string} filename - Filename for download
 */
function downloadBase64Image(base64Data, filename = 'image.png') {
    const link = document.createElement('a');
    link.href = base64Data;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Get current timestamp for filename
 * @returns {string} - Timestamp string
 */
function getTimestamp() {
    return new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
}

// Export for modules (if using)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        log,
        logError,
        logWarn,
        showError,
        showSuccess,
        hideMessage,
        showSpinner,
        optimizeImageForUpload,
        fileToBase64,
        apiRequest,
        isNotEmpty,
        isValidImage,
        isFileSizeValid,
        safeSetInnerHTML,
        safeSetValue,
        safeGetValue,
        downloadBase64Image,
        getTimestamp,
    };
}
