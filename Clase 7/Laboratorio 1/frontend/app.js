// SafetyVision Pro - Frontend JavaScript

// Global variables
let selectedFile = null;
let apiEndpoint = '';
let config = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await loadConfig();
        await initializeApp();
        setupEventListeners();
        await loadDashboardData();
    } catch (error) {
        console.error('Error initializing app:', error);
        showToast('Error al inicializar la aplicación', 'error');
    }
});

// Load configuration from config.json
async function loadConfig() {
    try {
        const response = await fetch('./config.json');
        if (!response.ok) {
            throw new Error('Failed to load config');
        }
        config = await response.json();
        apiEndpoint = config.apiEndpoint;
        console.log('Configuration loaded:', config);
    } catch (error) {
        console.error('Error loading config:', error);
        // Fallback for development
        apiEndpoint = 'https://your-api-endpoint.execute-api.eu-west-1.amazonaws.com/prod/';
        showToast('Error cargando configuración', 'error');
    }
}

// Initialize the application
async function initializeApp() {
    console.log('Initializing SafetyVision Pro...');
    
    // Set current date/time
    updateTimestamps();
    
    // Start auto-refresh
    setInterval(updateTimestamps, 60000); // Update every minute
}

// Setup event listeners
function setupEventListeners() {
    // Upload area drag and drop
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    if (uploadArea && fileInput) {
        // Click on upload area opens file dialog
        uploadArea.addEventListener('click', () => {
            console.log('Upload area clicked, opening file dialog');
            fileInput.click();
        });
        
        // File input change event
        fileInput.addEventListener('change', (event) => {
            console.log('File input changed');
            handleFileSelect(event);
        });
        
        // Drag and drop events
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
    }
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        document.addEventListener(eventName, preventDefaults, false);
    });
}

// Prevent default drag behaviors
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Handle drag over
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').classList.add('dragover');
}

// Handle drag leave
function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').classList.remove('dragover');
}

// Handle drop
function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect({ target: { files } });
    }
}

// Handle file selection
function handleFileSelect(event) {
    const files = event.target.files;
    if (files.length === 0) return;
    
    const file = files[0];
    
    // Validate file
    if (!validateFile(file)) {
        return;
    }
    
    selectedFile = file;
    showUploadForm();
    displaySelectedImage(file);
}

// Validate file
function validateFile(file) {
    // Check file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        showToast('Por favor, selecciona una imagen válida (JPG, PNG, GIF)', 'error');
        return false;
    }
    
    // Check file size (10MB max)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showToast('El archivo es demasiado grande. Máximo 10MB', 'error');
        return false;
    }
    
    return true;
}

// Show upload form
function showUploadForm() {
    document.getElementById('uploadForm').style.display = 'block';
}

// Display selected image
function displaySelectedImage(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        // Update upload area to show preview
        const uploadContent = document.querySelector('.upload-content');
        uploadContent.innerHTML = `
            <img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px; border-radius: 8px; margin-bottom: 1rem;">
            <h3>${file.name}</h3>
            <p>Formato: ${file.type}</p>
            <p>Tamaño: ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
        `;
    };
    reader.readAsDataURL(file);
}

// Cancel upload
function cancelUpload() {
    selectedFile = null;
    document.getElementById('uploadForm').style.display = 'none';
    document.getElementById('fileInput').value = '';
    
    // Reset upload content
    const uploadContent = document.querySelector('.upload-content');
    uploadContent.innerHTML = `
        <i class="fas fa-cloud-upload-alt upload-icon"></i>
        <h3>Arrastra una imagen aquí</h3>
        <p>o haz clic para seleccionar</p>
        <p class="upload-hint">Formatos: JPG, PNG, GIF (Máx. 10MB)</p>
    `;
}

// Upload image for analysis
async function uploadImage() {
    if (!selectedFile) {
        showToast('Por favor, selecciona una imagen', 'error');
        return;
    }
    
    const siteId = document.getElementById('siteId').value || 'unknown';
    const location = document.getElementById('location').value || 'unknown';
    
    showLoading('Subiendo imagen...');
    
    try {
        // Convert file to base64
        const base64 = await fileToBase64(selectedFile);
        
        // Upload image
        const uploadResponse = await fetch(`${apiEndpoint}upload`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image_data: base64,
                site_id: siteId,
                location: location,
                timestamp: new Date().toISOString()
            })
        });
        
        if (!uploadResponse.ok) {
            const error = await uploadResponse.json();
            throw new Error(error.error || 'Error uploading image');
        }
        
        const uploadResult = await uploadResponse.json();
        console.log('Upload successful:', uploadResult);
        
        showLoading('Analizando imagen con IA...');
        
        // Analyze image
        const analysisResponse = await fetch(`${apiEndpoint}analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image_id: uploadResult.image_id,
                s3_key: uploadResult.s3_key
            })
        });
        
        if (!analysisResponse.ok) {
            const error = await analysisResponse.json();
            throw new Error(error.error || 'Error analyzing image');
        }
        
        const analysisResult = await analysisResponse.json();
        console.log('Analysis successful:', analysisResult);
        
        hideLoading();
        displayAnalysisResults(analysisResult, selectedFile);
        
        // Refresh dashboard data
        await loadDashboardData();
        
        showToast('Análisis completado exitosamente', 'success');
        
        // Reset upload form
        cancelUpload();
        
    } catch (error) {
        console.error('Error uploading/analyzing image:', error);
        hideLoading();
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Convert file to base64
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result.split(',')[1]); // Remove data:image/...;base64, prefix
        reader.onerror = error => reject(error);
    });
}

// Display analysis results
function displayAnalysisResults(results, imageFile) {
    const resultsSection = document.getElementById('resultsSection');
    const resultImage = document.getElementById('resultImage');
    const scoreValue = document.getElementById('scoreValue');
    const scoreCircle = document.getElementById('scoreCircle');
    const ppeList = document.getElementById('ppeList');
    const violationsList = document.getElementById('violationsList');
    
    // Display image
    const reader = new FileReader();
    reader.onload = function(e) {
        resultImage.src = e.target.result;
    };
    reader.readAsDataURL(imageFile);
    
    // Display safety score
    scoreValue.textContent = `${results.safety_score}%`;
    
    // Update score circle color based on score
    if (results.safety_score >= 80) {
        scoreCircle.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
    } else if (results.safety_score >= 60) {
        scoreCircle.style.background = 'linear-gradient(135deg, #ffc107, #fd7e14)';
    } else {
        scoreCircle.style.background = 'linear-gradient(135deg, #dc3545, #c82333)';
    }
    
    // Display PPE detected
    ppeList.innerHTML = '';
    if (results.ppe_detected && Object.keys(results.ppe_detected).length > 0) {
        Object.entries(results.ppe_detected).forEach(([person, ppe]) => {
            const personDiv = document.createElement('div');
            personDiv.className = 'person-ppe';
            personDiv.innerHTML = `<strong>${person}:</strong>`;
            
            const ppeItems = document.createElement('div');
            ppeItems.style.marginLeft = '1rem';
            ppeItems.style.marginTop = '0.5rem';
            
            Object.entries(ppe).forEach(([item, detected]) => {
                const ppeItem = document.createElement('div');
                ppeItem.className = 'ppe-item';
                ppeItem.innerHTML = `
                    <i class="fas fa-${detected ? 'check' : 'times'}"></i>
                    ${getPPEDisplayName(item)}: ${detected ? 'Detectado' : 'No detectado'}
                `;
                ppeItems.appendChild(ppeItem);
            });
            
            personDiv.appendChild(ppeItems);
            ppeList.appendChild(personDiv);
        });
    } else {
        ppeList.innerHTML = '<p>No se detectaron personas con EPP</p>';
    }
    
    // Display violations
    violationsList.innerHTML = '';
    if (results.violations && results.violations.length > 0) {
        results.violations.forEach(violation => {
            const violationItem = document.createElement('div');
            violationItem.className = 'violation-item';
            violationItem.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                ${violation}
            `;
            violationsList.appendChild(violationItem);
        });
    } else {
        violationsList.innerHTML = '<div class="ppe-item"><i class="fas fa-check"></i>No se detectaron infracciones</div>';
    }
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Get PPE display name
function getPPEDisplayName(ppeKey) {
    const names = {
        'helmet': 'Casco',
        'vest': 'Chaleco',
        'gloves': 'Guantes',
        'glasses': 'Gafas',
        'boots': 'Botas'
    };
    return names[ppeKey] || ppeKey;
}

// Load dashboard data
async function loadDashboardData() {
    try {
        showLoading('Cargando datos del dashboard...');
        
        const response = await fetch(`${apiEndpoint}stats?days=7`);
        if (!response.ok) {
            throw new Error('Error loading dashboard data');
        }
        
        const data = await response.json();
        console.log('Dashboard data loaded:', data);
        
        updateStatsDisplay(data.summary);
        await loadRecentAnalyses();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showToast('Error cargando datos del dashboard', 'error');
    } finally {
        hideLoading();
    }
}

// Update stats display
function updateStatsDisplay(stats) {
    document.getElementById('totalImages').textContent = stats.analyzed_images || 0;
    document.getElementById('safetyScore').textContent = `${Math.round(stats.avg_safety_score || 0)}%`;
    document.getElementById('violations').textContent = stats.total_violations || 0;
    document.getElementById('complianceRate').textContent = `${Math.round(stats.compliance_rate || 0)}%`;
}

// Load recent analyses
async function loadRecentAnalyses() {
    try {
        const response = await fetch(`${apiEndpoint}dashboard`);
        if (!response.ok) {
            throw new Error('Error loading recent analyses');
        }
        
        const data = await response.json();
        displayRecentAnalyses(data.recent_analyses || []);
        
    } catch (error) {
        console.error('Error loading recent analyses:', error);
        // Don't show toast for this error as it's not critical
    }
}

// Display recent analyses
function displayRecentAnalyses(analyses) {
    const recentGrid = document.getElementById('recentGrid');
    
    if (analyses.length === 0) {
        recentGrid.innerHTML = '<p>No hay análisis recientes</p>';
        return;
    }
    
    recentGrid.innerHTML = '';
    analyses.forEach(analysis => {
        const card = createRecentAnalysisCard(analysis);
        recentGrid.appendChild(card);
    });
}

// Create recent analysis card
function createRecentAnalysisCard(analysis) {
    const card = document.createElement('div');
    card.className = 'recent-card';
    
    const scoreClass = analysis.safety_score >= 80 ? 'score-high' : 
                      analysis.safety_score >= 60 ? 'score-medium' : 'score-low';
    
    const analysisTime = new Date(analysis.analyzed_at).toLocaleString('es-ES');
    
    card.innerHTML = `
        <div class="recent-card-content">
            <div class="recent-card-header">
                <span class="recent-card-title">${analysis.site_id}</span>
                <span class="recent-card-score ${scoreClass}">${analysis.safety_score}%</span>
            </div>
            <div class="recent-card-details">
                <div class="recent-card-detail">
                    <i class="fas fa-map-marker-alt"></i>
                    ${analysis.location}
                </div>
                <div class="recent-card-detail">
                    <i class="fas fa-clock"></i>
                    ${analysisTime}
                </div>
                <div class="recent-card-detail">
                    <i class="fas fa-exclamation-triangle"></i>
                    ${analysis.violations_count} infracciones
                </div>
            </div>
        </div>
    `;
    
    return card;
}

// Refresh data
async function refreshData() {
    await loadDashboardData();
    showToast('Datos actualizados', 'info');
}

// Update timestamps
function updateTimestamps() {
    const now = new Date();
    // Update any timestamp displays if needed
}

// Show loading overlay
function showLoading(message = 'Cargando...') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingMessage = document.getElementById('loadingMessage');
    
    loadingMessage.textContent = message;
    overlay.style.display = 'flex';
}

// Hide loading overlay
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = 'none';
}

// Show toast notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = getToastIcon(type);
    toast.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 5000);
}

// Get toast icon based on type
function getToastIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Utility functions
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Error handling
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    showToast('Ha ocurrido un error inesperado', 'error');
});

// Unhandled promise rejection
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    showToast('Ha ocurrido un error inesperado', 'error');
});

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        loadConfig,
        uploadImage,
        loadDashboardData,
        showToast
    };
}
