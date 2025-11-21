// ============================================
// PLANNING DETAIL RENDER - Frontend JavaScript
// Version: 1.0
// ============================================

// ============== CONFIG ==============
const API_BASE_URL = 'http://localhost:5001/api';

// ============== STATE ==============
let currentSketchImage = null;
let currentRenderedImage = null;
let isRendering = false;

// ============== DOM ELEMENTS ==============
const uploadSketch = document.getElementById('uploadSketch');
const previewImage = document.getElementById('previewImage');
const uploadLabel = document.getElementById('uploadLabel');
const generateButton = document.getElementById('generateRenderButton');
const gallery = document.getElementById('gallery');
const aspectRatioSelect = document.getElementById('aspect_ratio');

// ============== INIT ==============
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Planning Detail Render v1.0 initialized');
    setupEventListeners();
});

// ============== EVENT LISTENERS ==============
function setupEventListeners() {
    // File upload
    uploadSketch.addEventListener('change', handleImageUpload);

    // Click preview to re-upload
    previewImage.addEventListener('click', () => uploadSketch.click());

    // Generate button
    generateButton.addEventListener('click', generateRender);

    // Download button
    document.addEventListener('click', (e) => {
        if (e.target.closest('#downloadImageBtn')) {
            handleDownloadImage();
        }
    });

    // Regenerate button
    document.addEventListener('click', (e) => {
        if (e.target.closest('#regenerateBtn')) {
            generateRender();
        }
    });

    // Range slider display
    const sketchAdherence = document.getElementById('sketch_adherence');
    const sketchAdherenceValue = document.getElementById('sketch_adherence_value');
    if (sketchAdherence && sketchAdherenceValue) {
        sketchAdherence.addEventListener('input', (e) => {
            sketchAdherenceValue.textContent = e.target.value;
        });
    }
}

// ============== IMAGE UPLOAD ==============
async function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    console.log(`📁 Uploading ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);

    try {
        // Read file as base64
        const reader = new FileReader();
        reader.onload = (e) => {
            const base64 = e.target.result;
            currentSketchImage = base64;

            // Show preview
            previewImage.src = base64;
            previewImage.classList.remove('hidden');
            uploadLabel.classList.add('hidden');

            // Enable generate button
            generateButton.disabled = false;

            console.log('✅ Image uploaded successfully');
        };
        reader.readAsDataURL(file);
    } catch (error) {
        console.error('❌ Image upload failed:', error);
        showError('renderError', 'Lỗi khi tải ảnh: ' + error.message);
    }
}

// ============== COLLECT FORM DATA ==============
function collectFormData() {
    const qualityPresets = {
        global_illumination: document.getElementById('quality_gi').checked,
        soft_shadows: document.getElementById('quality_shadows').checked,
        hdri_sky: document.getElementById('quality_hdri').checked,
        reflections: document.getElementById('quality_reflection').checked,
        depth_of_field: document.getElementById('quality_dof').checked,
        bloom: document.getElementById('quality_bloom').checked,
        color_correction: document.getElementById('quality_color_correction').checked,
        desaturate: document.getElementById('quality_desaturate').checked
    };

    return {
        planning_description: document.getElementById('planning_description').value,
        camera_angle: document.getElementById('camera_angle').value,
        time_of_day: document.getElementById('time_of_day').value,
        weather: document.getElementById('weather').value,
        quality_presets: qualityPresets,
        sketch_adherence: parseFloat(document.getElementById('sketch_adherence').value),
        aspect_ratio: aspectRatioSelect.value
    };
}

// ============== GENERATE RENDER ==============
async function generateRender() {
    if (!currentSketchImage) {
        showError('renderError', 'Vui lòng upload sketch trước!');
        return;
    }

    if (isRendering) {
        console.warn('⚠️  Rendering already in progress');
        return;
    }

    // Validate required fields
    const planningDesc = document.getElementById('planning_description').value.trim();
    if (!planningDesc) {
        showError('renderError', 'Vui lòng điền mô tả tổng thể quy hoạch!');
        return;
    }

    isRendering = true;
    showSpinner('renderSpinner', true);
    generateButton.disabled = true;
    hideError('renderError');
    hideSuccess('renderSuccess');

    try {
        console.log('🎨 Generating planning detail render...');

        const formData = collectFormData();
        console.log('📝 Form data:', formData);

        const requestData = {
            image_base64: currentSketchImage,
            planning_data: formData
        };

        const startTime = Date.now();

        const response = await fetch(`${API_BASE_URL}/planning/detail-render`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Server error: ${response.status}`);
        }

        const data = await response.json();
        const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(1);

        console.log(`✅ Render generated in ${elapsedTime}s`);

        // Display result
        currentRenderedImage = data.generated_image_base64;
        displayRenderedImage(currentRenderedImage);

        showSuccess('renderSuccess', `✅ Render thành công trong ${elapsedTime}s!`);

        // Show stats
        document.getElementById('statTime').textContent = `${elapsedTime}s`;
        document.getElementById('statsBox').classList.remove('hidden');

    } catch (error) {
        console.error('❌ Render failed:', error);
        showError('renderError', 'Lỗi khi render: ' + error.message);
    } finally {
        isRendering = false;
        showSpinner('renderSpinner', false);
        generateButton.disabled = false;
    }
}

// ============== DISPLAY RESULTS ==============
function displayRenderedImage(base64Image) {
    gallery.innerHTML = '';

    const img = document.createElement('img');
    img.src = base64Image;
    img.alt = 'Rendered planning';
    img.style.width = '100%';
    img.style.borderRadius = '12px';
    img.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';

    gallery.appendChild(img);

    // Show output controls
    document.getElementById('outputControls').classList.remove('hidden');
}

// ============== DOWNLOAD ==============
function handleDownloadImage() {
    if (!currentRenderedImage) {
        showError('renderError', 'Chưa có ảnh để tải về!');
        return;
    }

    const link = document.createElement('a');
    link.href = currentRenderedImage;
    link.download = `planning-detail-render-${Date.now()}.png`;
    link.click();

    console.log('📥 Image downloaded');
    showSuccess('renderSuccess', '✅ Đã tải ảnh về!');
}

// ============== UI HELPERS ==============
function showError(elementId, message) {
    const el = document.getElementById(elementId);
    if (el) {
        el.textContent = message;
        el.classList.remove('hidden');
    }
}

function hideError(elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        el.classList.add('hidden');
    }
}

function showSuccess(elementId, message) {
    const el = document.getElementById(elementId);
    if (el) {
        el.textContent = message;
        el.classList.remove('hidden');
    }
}

function hideSuccess(elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        el.classList.add('hidden');
    }
}

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
