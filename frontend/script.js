// ============================================
// ARCHITECTURE S2R TOOL - Frontend JavaScript
// Version: 3.0 - WITH REFERENCE IMAGE SUPPORT
// Updated: 2025-11-01
// ============================================

// ============== CONFIG ==============
const API_BASE_URL = 'http://localhost:5001/api';

// ============== STATE ==============
let currentSketchImage = null;
let currentAnalysisData = null;
let currentTranslatedData = null;
let currentRenderedImage = null;
let currentReferenceImage = null; // ⭐ NEW: Reference image storage

// ============== DOM ELEMENTS ==============
const uploadSketch = document.getElementById('uploadSketch');
const previewImage = document.getElementById('previewImage');
const uploadLabel = document.getElementById('uploadLabel');
const analyzeButton = document.getElementById('analyzeSketchButton');
const generateButton = document.getElementById('generateRenderButton');
const gallery = document.getElementById('gallery');
const aspectRatioSelect = document.getElementById('aspect_ratio');
const viewpointSelect = document.getElementById('viewpoint');

// ============== INIT ==============
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 S2R Tool v3.0 initialized');
    loadAspectRatios();
    setupEventListeners();
    setupDynamicContainers();
    setupExportButton();
    setupReferenceImageUI(); // ⭐ NEW
});

// ============== ASPECT RATIOS ==============
async function loadAspectRatios() {
    const ratios = {
        "1:1": "Vuông (1024×1024)",
        "3:4": "Chân dung (768×1024)",
        "4:3": "Tiêu chuẩn (1024×768)",
        "9:16": "Dọc (576×1024)",
        "16:9": "Widescreen (1024×576)"
    };
    
    aspectRatioSelect.innerHTML = '';
    for (const [value, label] of Object.entries(ratios)) {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = label;
        if (value === "16:9") option.selected = true;
        aspectRatioSelect.appendChild(option);
    }
}

// ============== EVENT LISTENERS ==============
function setupEventListeners() {
    // File upload
    uploadSketch.addEventListener('change', handleImageUpload);
    
    // Click preview to re-upload
    previewImage.addEventListener('click', () => uploadSketch.click());
    
    // Analyze button
    analyzeButton.addEventListener('click', analyzeSketch);
    
    // Generate button
    generateButton.addEventListener('click', generateRender);
    
    // Range slider display
    const sketchAdherence = document.getElementById('sketch_adherence');
    const sketchAdherenceValue = document.getElementById('sketch_adherence_value');
    if (sketchAdherence && sketchAdherenceValue) {
        sketchAdherence.addEventListener('input', (e) => {
            sketchAdherenceValue.textContent = e.target.value;
        });
    }
    
    // Add dynamic item buttons
    document.querySelectorAll('.btn-add').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const container = document.getElementById(e.target.dataset.container);
            const type = e.target.dataset.type;
            addDynamicItem(container, type);
        });
    });
}

// ============== IMAGE UPLOAD ==============
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        currentSketchImage = e.target.result;
        previewImage.src = e.target.result;
        previewImage.classList.remove('hidden');
        uploadLabel.classList.add('hidden');
        analyzeButton.disabled = false;
        
        console.log('✅ Image uploaded');
    };
    reader.readAsDataURL(file);
}

// ============== STEP 1: ANALYZE SKETCH ==============
async function analyzeSketch() {
    if (!currentSketchImage) {
        alert('Vui lòng upload ảnh sketch trước!');
        return;
    }
    
    showSpinner('analyzeSpinner', true);
    analyzeButton.disabled = true;
    hideError('analyzeError');
    
    // SỬA LỖI: Chúng ta sẽ cấu trúc lại toàn bộ khối try/catch
    // để xử lý response một cách chính xác và chỉ đọc body 1 LẦN.
    try {
        console.log('📊 Analyzing sketch...');
        
        const response = await fetch(`${API_BASE_URL}/analyze-sketch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image_base64: currentSketchImage
            })
        });
        
        // --- LOGIC SỬA LỖI BẮT ĐẦU ---

        // Kiểm tra xem response có OK hay không *TRƯỚC KHI* đọc body
        if (!response.ok) {
            // Nếu là lỗi (500, 404, 400, v.v.)
            let errorMsg = `HTTP ${response.status}: ${response.statusText}`;
            try {
                // Đọc body lỗi (ĐỌC LẦN 1)
                const errorData = await response.json();
                if (errorData && errorData.error) {
                    errorMsg = errorData.error; // Lấy lỗi chi tiết từ backend
                }
            } catch (jsonError) {
                // Backend trả về lỗi 500 nhưng không phải JSON
                console.warn("Could not parse error JSON from backend", jsonError);
            }
            // Văng lỗi để nhảy xuống khối catch bên ngoài
            throw new Error(errorMsg);
        }
        
        // Nếu chúng ta đến được đây, nghĩa là response.ok == true (200)
        // Đọc body thành công (ĐỌC LẦN 1)
        currentAnalysisData = await response.json();

        // --- LOGIC SỬA LỖI KẾT THÚC ---

        console.log('✅ Analysis complete:', currentAnalysisData);
        
        // Auto-fill form với dữ liệu phân tích
        fillFormFromAnalysis(currentAnalysisData);
        
        // Tự động translate
        await translatePrompt();
        
        alert('Phân tích thành công! Vui lòng kiểm tra và chỉnh sửa thông số.');
        
    } catch (error) {
        console.error('❌ Analysis failed:', error);
        // Khối catch này bây giờ sẽ bắt cả lỗi mạng VÀ lỗi 500 mà chúng ta đã văng ra
        showError('analyzeError', `Lỗi phân tích: ${error.message}`);

    } finally {
        showSpinner('analyzeSpinner', false);
        analyzeButton.disabled = false;
    }
}

// ============== FILL FORM FROM ANALYSIS ==============
function fillFormFromAnalysis(data) {
    // Main description
    document.getElementById('main_description').value = 
        `${data.building_type || ''} - ${data.facade_style || ''}`;
    
    // Critical elements
    const criticalContainer = document.getElementById('criticalElementsContainer');
    criticalContainer.innerHTML = '';
    if (data.critical_elements) {
        data.critical_elements.forEach(elem => {
            addDynamicItem(criticalContainer, 'element', elem.type, elem.description);
        });
    }
    
    // Materials
    const materialsContainer = document.getElementById('materialsPreciseContainer');
    materialsContainer.innerHTML = '';
    if (data.materials_precise) {
        data.materials_precise.forEach(mat => {
            addDynamicItem(materialsContainer, 'material', mat.type, mat.description);
        });
    }
    
    // Environment
    const envContainer = document.getElementById('environmentContainer');
    envContainer.innerHTML = '';
    if (data.environment) {
        data.environment.forEach(env => {
            addDynamicItem(envContainer, 'setting', env.type, env.description);
        });
    }
    
    // Technical specs
    if (data.technical_specs) {
        document.getElementById('tech_camera').value = data.technical_specs.camera || '';
        document.getElementById('tech_lens').value = data.technical_specs.lens || '';
        document.getElementById('tech_lighting').value = data.technical_specs.lighting || '';
        document.getElementById('tech_perspective').value = data.technical_specs.perspective || '';
    }
}

// ============== STEP 2: TRANSLATE PROMPT ==============
async function translatePrompt() {
    const formData = collectFormData();
    
    try {
        console.log('🌐 Translating to English...');
        
        const response = await fetch(`${API_BASE_URL}/translate-prompt`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                form_data: formData
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        currentTranslatedData = result.translated_data_en;
        console.log('✅ Translation complete');
        
        // Enable generate button
        generateButton.disabled = false;
        
    } catch (error) {
        console.error('❌ Translation failed:', error);
        throw error;
    }
}

// ============== COLLECT FORM DATA ==============
function collectFormData() {
    const data = {
        building_type: document.getElementById('main_description').value,
        facade_style: document.getElementById('main_description').value,
        sketch_detail_level: currentAnalysisData?.sketch_detail_level || 'intermediate',
        is_colored: currentAnalysisData?.is_colored || false,
        critical_elements: [],
        materials_precise: [],
        environment: [],
        style_keywords: document.getElementById('style_keywords').value,
        technical_specs: {
            camera: document.getElementById('tech_camera').value,
            lens: document.getElementById('tech_lens').value,
            perspective: document.getElementById('tech_perspective').value,
            lighting: document.getElementById('tech_lighting').value
        },
        negative_prompt: document.getElementById('negative_prompt').value,
        sketch_adherence: parseFloat(document.getElementById('sketch_adherence').value)
    };
    
    // Collect critical elements
    document.querySelectorAll('#criticalElementsContainer .dynamic-item').forEach(item => {
        data.critical_elements.push({
            type: item.querySelector('.item-type').value,
            description: item.querySelector('.item-description').value
        });
    });
    
    // Collect materials
    document.querySelectorAll('#materialsPreciseContainer .dynamic-item').forEach(item => {
        data.materials_precise.push({
            type: item.querySelector('.item-type').value,
            description: item.querySelector('.item-description').value
        });
    });
    
    // Collect environment
    document.querySelectorAll('#environmentContainer .dynamic-item').forEach(item => {
        data.environment.push({
            type: item.querySelector('.item-type').value,
            description: item.querySelector('.item-description').value
        });
    });
    
    return data;
}

// ============== STEP 3: GENERATE RENDER ==============

async function generateRender() {
    if (!currentSketchImage || !currentTranslatedData) {
        alert('Vui lòng hoàn thành phân tích trước!');
        return;
    }
    
    showSpinner('renderSpinner', true);
    generateButton.disabled = true;
    hideError('renderError');
    
    try {
        console.log('🎨 Generating render...');
        
        // ✅ FIX: Collect CURRENT form data (with user edits)
        const formDataVi = collectFormData();
        
        // ⭐ Build request body with optional reference
        const requestBody = {
            image_base64: currentSketchImage,
            form_data_vi: formDataVi,  // ✅ CHANGED: Send current form data
            aspect_ratio: aspectRatioSelect.value,
            viewpoint: viewpointSelect.value
        };
        
        // ⭐ Add reference image if selected
        if (currentReferenceImage) {
            requestBody.reference_image_base64 = currentReferenceImage;
            console.log('📎 Using reference image for style consistency');
        }
        
        console.log('📤 Sending form_data_vi (with user edits)');
        
        const response = await fetch(`${API_BASE_URL}/render`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Render failed');
        }
        
        const result = await response.json();
        currentRenderedImage = result.generated_image_base64;
        
        console.log('✅ Render complete');
        
        // Display result
        displayRenderedImage(currentRenderedImage, result.mime_type);
        
        alert('Render thành công! ✨');
        
    } catch (error) {
        console.error('❌ Render failed:', error);
        showError('renderError', `Lỗi render: ${error.message}`);
    } finally {
        showSpinner('renderSpinner', false);
        generateButton.disabled = false;
    }
}

// ============== DISPLAY RENDERED IMAGE ==============
function displayRenderedImage(base64Data, mimeType) {
    gallery.innerHTML = '';
    
    const img = document.createElement('img');
    img.src = `data:${mimeType};base64,${base64Data}`;
    img.alt = 'Rendered result';
    img.style.width = '100%';
    img.style.height = '100%';
    img.style.objectFit = 'contain';
    
    gallery.appendChild(img);
    
    // Show output controls
    document.getElementById('outputControls').classList.remove('hidden');
}

// ============== DYNAMIC ITEMS (Elements, Materials, Environment) ==============
function addDynamicItem(container, type, typeValue = '', descValue = '') {
    const div = document.createElement('div');
    div.className = 'dynamic-item';
    
    const typePlaceholder = type === 'element' ? 'VD: Cửa sổ' : 
                            type === 'material' ? 'VD: Tường' : 'VD: Cây xanh';
    const descPlaceholder = type === 'element' ? 'Mô tả chi tiết' : 
                             type === 'material' ? 'Bê tông xám sáng' : 'Nhiều cây xanh';
    
    div.innerHTML = `
        <input type="text" class="item-type" placeholder="${typePlaceholder}" value="${typeValue}">
        <input type="text" class="item-description" placeholder="${descPlaceholder}" value="${descValue}">
        <button type="button" class="btn-remove" onclick="this.parentElement.remove()">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
    `;
    
    container.appendChild(div);
}

function setupDynamicContainers() {
    // Initialize với 1 item mỗi container
    const criticalContainer = document.getElementById('criticalElementsContainer');
    const materialsContainer = document.getElementById('materialsPreciseContainer');
    const envContainer = document.getElementById('environmentContainer');
    
    if (criticalContainer.children.length === 0) {
        addDynamicItem(criticalContainer, 'element');
    }
    if (materialsContainer.children.length === 0) {
        addDynamicItem(materialsContainer, 'material');
    }
    if (envContainer.children.length === 0) {
        addDynamicItem(envContainer, 'setting');
    }
}

// ============== ⭐ NEW: REFERENCE IMAGE SYSTEM ==============

function setupReferenceImageUI() {
    // Create reference image section in form
    const formPanel = document.querySelector('.panel-form form');
    
    const referenceSection = document.createElement('details');
    referenceSection.className = 'form-section';
    referenceSection.id = 'referenceSection';
    referenceSection.innerHTML = `
        <summary>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
            Ảnh Tham Khảo (Reference) ⭐
        </summary>
        <div class="section-content">
            <p style="font-size: 0.875rem; color: #64748b; margin-bottom: 1rem;">
                Sử dụng ảnh tham khảo để giữ style/màu sắc nhất quán khi render góc khác hoặc phiên bản mới.
            </p>
            
            <!-- Reference Preview -->
            <div id="referencePreview" class="reference-preview hidden">
                <img id="referencePreviewImage" src="" alt="Reference">
                <button type="button" id="clearReferenceBtn" class="btn-remove">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
            </div>
            
            <!-- Upload Reference -->
            <div class="form-group">
                <label for="uploadReference">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                    Upload từ máy tính
                </label>
                <input type="file" id="uploadReference" accept="image/*" style="display: none;">
                <button type="button" id="uploadReferenceBtn" class="btn-secondary">
                    Chọn ảnh Reference
                </button>
            </div>
            
            <!-- Browse Library -->
            <div class="form-group">
                <label>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M20.4 14.5L16 10 4 20"/></svg>
                    Hoặc chọn từ thư viện
                </label>
                <button type="button" id="browseLibraryBtn" class="btn-secondary">
                    Duyệt Reference Library
                </button>
            </div>
        </div>
    `;
    
    // Insert before style keywords section
    const styleSection = Array.from(formPanel.querySelectorAll('.form-section')).find(
        section => section.textContent.includes('Từ khóa Phong cách')
    );
    
    if (styleSection) {
        formPanel.insertBefore(referenceSection, styleSection);
    } else {
        formPanel.appendChild(referenceSection);
    }
    
    // Setup event listeners
    document.getElementById('uploadReferenceBtn').addEventListener('click', () => {
        document.getElementById('uploadReference').click();
    });
    
    document.getElementById('uploadReference').addEventListener('change', handleReferenceUpload);
    document.getElementById('browseLibraryBtn').addEventListener('click', openReferenceLibrary);
    document.getElementById('clearReferenceBtn')?.addEventListener('click', clearReference);
}

function handleReferenceUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        currentReferenceImage = e.target.result;
        showReferencePreview(e.target.result);
        console.log('✅ Reference image uploaded');
        alert('Đã tải ảnh reference! Render tiếp sẽ giữ style từ ảnh này.');
    };
    reader.readAsDataURL(file);
}

function showReferencePreview(imageSrc) {
    const preview = document.getElementById('referencePreview');
    const img = document.getElementById('referencePreviewImage');
    
    img.src = imageSrc;
    preview.classList.remove('hidden');
}

function clearReference() {
    currentReferenceImage = null;
    document.getElementById('referencePreview').classList.add('hidden');
    document.getElementById('uploadReference').value = '';
    console.log('🗑️ Reference cleared');
}

async function openReferenceLibrary() {
    try {
        // Fetch available references
        const response = await fetch(`${API_BASE_URL}/references/list`);
        
        if (!response.ok) {
            throw new Error('Failed to load library');
        }
        
        const data = await response.json();
        
        if (data.categories) {
            // Show category selection
            showCategoryPicker(data.categories);
        } else if (data.images) {
            // Show images directly
            showReferencePicker(data.images);
        }
        
    } catch (error) {
        console.error('❌ Library load failed:', error);
        alert('Không thể tải thư viện reference. Vui lòng kiểm tra backend.');
    }
}

function showCategoryPicker(categories) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Chọn Danh Mục Reference</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <div class="category-grid">
                    ${categories.map(cat => `
                        <button class="category-card" data-category="${cat}">
                            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="3" width="18" height="18" rx="2"/>
                                <circle cx="8.5" cy="8.5" r="1.5"/>
                                <path d="M20.4 14.5L16 10 4 20"/>
                            </svg>
                            <span>${cat}</span>
                        </button>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Event listeners
    modal.querySelector('.modal-close').addEventListener('click', () => modal.remove());
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
    
    modal.querySelectorAll('.category-card').forEach(card => {
        card.addEventListener('click', async () => {
            const category = card.dataset.category;
            modal.remove();
            
            // Fetch images in this category
            const response = await fetch(`${API_BASE_URL}/references/list?category=${category}`);
            const data = await response.json();
            showReferencePicker(data.images);
        });
    });
}

function showReferencePicker(images) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content modal-large">
            <div class="modal-header">
                <h3>Chọn Ảnh Reference</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <div class="reference-grid">
                    ${images.map(img => `
                        <div class="reference-card" data-image-id="${img.id}">
                            <img src="${img.thumbnail_url || '/api/references/serve/' + img.id}" alt="${img.name}">
                            <div class="reference-card-title">${img.name}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Event listeners
    modal.querySelector('.modal-close').addEventListener('click', () => modal.remove());
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
    
    modal.querySelectorAll('.reference-card').forEach(card => {
        card.addEventListener('click', async () => {
            const imageId = card.dataset.imageId;
            await selectReferenceFromLibrary(imageId);
            modal.remove();
        });
    });
}

async function selectReferenceFromLibrary(imageId) {
    try {
        const response = await fetch(`${API_BASE_URL}/references/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_id: imageId })
        });
        
        if (!response.ok) {
            throw new Error('Failed to download reference');
        }
        
        const data = await response.json();
        currentReferenceImage = `data:${data.mime_type};base64,${data.base64}`;
        showReferencePreview(currentReferenceImage);
        
        console.log('✅ Reference selected from library:', imageId);
        alert('Đã chọn reference từ thư viện!');
        
    } catch (error) {
        console.error('❌ Reference download failed:', error);
        alert('Không thể tải ảnh reference. Vui lòng thử lại.');
    }
}

// ⭐ Add "Use as Reference" button to output controls
function addUseAsReferenceButton() {
    const controls = document.getElementById('outputControls');
    
    // Check if button already exists
    if (document.getElementById('useAsReferenceBtn')) return;
    
    const btn = document.createElement('button');
    btn.id = 'useAsReferenceBtn';
    btn.className = 'btn-secondary btn-icon';
    btn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
            <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
        </svg>
        Làm Reference
    `;
    
    btn.addEventListener('click', () => {
        if (!currentRenderedImage) {
            alert('Chưa có ảnh render!');
            return;
        }
        
        currentReferenceImage = `data:image/png;base64,${currentRenderedImage}`;
        showReferencePreview(currentReferenceImage);
        
        // Open reference section
        document.getElementById('referenceSection').setAttribute('open', '');
        
        alert('✅ Đã lưu ảnh này làm reference!\nRender tiếp sẽ giữ style từ ảnh này.');
        console.log('📎 Current render saved as reference');
    });
    
    controls.appendChild(btn);
}

// Call this after displaying rendered image
function displayRenderedImageWithControls(base64Data, mimeType) {
    displayRenderedImage(base64Data, mimeType);
    addUseAsReferenceButton(); // ⭐ Add the button
}

// ============== EXPORT JSON ==============
function setupExportButton() {
    const exportBtn = document.createElement('button');
    exportBtn.id = 'exportJsonButton';
    exportBtn.className = 'btn-secondary';
    exportBtn.innerHTML = `
        <span id="exportSpinner" class="spinner hidden"></span>
        Export JSON
    `;
    exportBtn.addEventListener('click', exportToJSON);
    
    // Insert before generate button
    const outputActions = document.querySelector('.output-actions');
    outputActions.insertBefore(exportBtn, generateButton);
}

function exportToJSON() {
    if (!currentTranslatedData) {
        alert('Chưa có dữ liệu để export! Vui lòng phân tích sketch trước.');
        return;
    }
    
    const exportData = {
        sketch_info: {
            uploaded: currentSketchImage ? true : false,
            analysis: currentAnalysisData
        },
        form_data_vi: collectFormData(),
        translated_data_en: currentTranslatedData,
        reference_image: currentReferenceImage ? 'included' : 'none', // ⭐ Include ref status
        settings: {
            aspect_ratio: aspectRatioSelect.value,
            viewpoint: viewpointSelect.value,
            sketch_adherence: parseFloat(document.getElementById('sketch_adherence').value)
        },
        export_date: new Date().toISOString()
    };
    
    // Download as JSON file
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `s2r-data-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    console.log('✅ JSON exported');
}

// ============== HELPER FUNCTIONS ==============
function showSpinner(id, show) {
    const spinner = document.getElementById(id);
    if (spinner) {
        spinner.classList.toggle('hidden', !show);
    }
}

function showError(id, message) {
    const errorDiv = document.getElementById(id);
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }
}

function hideError(id) {
    const errorDiv = document.getElementById(id);
    if (errorDiv) {
        errorDiv.classList.add('hidden');
    }
}

// ============== END ==============
console.log('📦 Script v3.0 loaded successfully - Reference Image support enabled! 🎉');