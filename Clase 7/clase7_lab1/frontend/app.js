class SafetyDetectionApp {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.analysisHistory = [];
    }

    initializeElements() {
        // Upload elements
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.previewSection = document.getElementById('previewSection');
        this.previewImage = document.getElementById('previewImage');
        this.clearBtn = document.getElementById('clearBtn');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.uploadProgress = document.getElementById('uploadProgress');

        // Results elements
        this.resultsSection = document.getElementById('resultsSection');
        this.complianceCard = document.getElementById('complianceCard');
        this.complianceTitle = document.getElementById('complianceTitle');
        this.complianceDescription = document.getElementById('complianceDescription');
        this.complianceIcon = document.getElementById('complianceIcon');
        this.complianceBar = document.getElementById('complianceBar');
        this.compliancePercentage = document.getElementById('compliancePercentage');
        this.safetyItems = document.getElementById('safetyItems');
        this.allLabels = document.getElementById('allLabels');
        this.historyList = document.getElementById('historyList');
    }

    bindEvents() {
        // Upload events
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        this.clearBtn.addEventListener('click', () => this.clearImage());
        this.analyzeBtn.addEventListener('click', () => this.analyzeImage());

        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
    }

    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }

    processFile(file) {
        // Validate file type
        if (!file.type.match('image.*')) {
            this.showNotification('Por favor selecciona un archivo de imagen válido', 'error');
            return;
        }

        // Validate file size (10MB max)
        if (file.size > 10 * 1024 * 1024) {
            this.showNotification('El archivo no debe superar los 10MB', 'error');
            return;
        }

        this.currentFile = file;
        this.displayImage(file);
    }

    displayImage(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.previewImage.src = e.target.result;
            this.previewSection.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }

    clearImage() {
        this.previewSection.classList.add('hidden');
        this.resultsSection.classList.add('hidden');
        this.fileInput.value = '';
        this.currentFile = null;
    }

    async analyzeImage() {
        if (!this.currentFile) return;

        this.showProgress(true);
        this.analyzeBtn.disabled = true;

        try {
            // Convert image to base64
            const base64Image = await this.fileToBase64(this.currentFile);
            
            // Call API Gateway endpoint
            const response = await this.callAnalysisAPI(base64Image);
            
            // Process results
            this.displayResults(response);
            
            // Add to history
            this.addToHistory(response);
            
        } catch (error) {
            console.error('Error analyzing image:', error);
            this.showNotification('Error al analizar la imagen. Por favor intenta nuevamente.', 'error');
        } finally {
            this.showProgress(false);
            this.analyzeBtn.disabled = false;
        }
    }

    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => {
                // Remove data:image/jpeg;base64, prefix
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = error => reject(error);
        });
    }

    async callAnalysisAPI(base64Image) {
        // API Gateway endpoint
        const apiUrl = 'https://4daadw7mjl.execute-api.us-east-1.amazonaws.com/prod/analyze';
        
        console.log('🚀 Llamando a API Gateway:', apiUrl);
        
        // Crear una petición simple que no requiere preflight
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'text/plain', // Usar text/plain para evitar preflight
            },
            body: JSON.stringify({
                image: base64Image,
                filename: this.currentFile.name
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Error de API Gateway:', response.status,(xhr => xhr.responseText));
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }

        const result = await response.json();
        console.log('✅ Respuesta de API Gateway:', result);
        return result;
    }

    getMockAnalysisResult() {
        // Simulate API delay
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    imageId: 'img_' + Date.now(),
                    timestamp: new Date().toISOString(),
                    compliance: {
                        score: 67,
                        status: 'INCUMPLIMIENTO MODERADO',
                        level: 'medium'
                    },
                    safetyItems: {
                        helmet: true,
                        glasses: false,
                        gloves: true,
                        vest: true,
                        footwear: true
                    },
                    labels: [
                        { name: 'Person', confidence: 100 },
                        { name: 'Worker', confidence: 100 },
                        { name: 'Helmet', confidence: 99.8 },
                        { name: 'Glove', confidence: 95.2 },
                        { name: 'Vest', confidence: 87.5 },
                        { name: 'Footwear', confidence: 92.1 },
                        { name: 'Construction', confidence: 78.3 }
                    ]
                });
            }, 2000);
        });
    }

    displayResults(result) {
        this.resultsSection.classList.remove('hidden');

        // Display compliance status
        this.displayCompliance(result.compliance);

        // Display safety items
        this.displaySafetyItems(result.safetyItems);

        // Display all labels
        this.displayLabels(result.labels);
    }

    displayCompliance(compliance) {
        const { score, status, level } = compliance;
        
        // Set card styling based on compliance level
        this.complianceCard.className = 'rounded-lg p-6 text-white';
        
        if (level === 'high') {
            this.complianceCard.classList.add('compliance-high');
            this.complianceIcon.className = 'fas fa-check-circle';
        } else if (level === 'medium') {
            this.complianceCard.classList.add('compliance-medium');
            this.complianceIcon.className = 'fas fa-exclamation-triangle';
        } else {
            this.complianceCard.classList.add('compliance-low');
            this.complianceIcon.className = 'fas fa-times-circle';
        }

        this.complianceTitle.textContent = status;
        this.complianceDescription.textContent = `Puntuación: ${score}%`;
        this.complianceBar.style.width = `${score}%`;
        this.compliancePercentage.textContent = `${score}% de cumplimiento de requisitos obligatorios`;
    }

    displaySafetyItems(safetyItems) {
        const items = [
            { key: 'helmet', name: 'Casco', icon: 'fa-hard-hat' },
            { key: 'glasses', name: 'Gafas', icon: 'fa-glasses' },
            { key: 'gloves', name: 'Guantes', icon: 'fa-mitten' },
            { key: 'vest', name: 'Chaleco', icon: 'fa-vest' },
            { key: 'footwear', name: 'Calzado', icon: 'fa-shoe-prints' }
        ];

        this.safetyItems.innerHTML = items.map(item => `
            <div class="safety-item text-center p-4 rounded-lg border-2 ${
                safetyItems[item.key] 
                    ? 'border-green-500 bg-green-50 text-green-700' 
                    : 'border-red-500 bg-red-50 text-red-700'
            }">
                <i class="fas ${item.icon} text-2xl mb-2"></i>
                <p class="font-medium">${item.name}</p>
                <p class="text-sm mt-1">
                    ${safetyItems[item.key] ? 'Detectado' : 'No detectado'}
                </p>
            </div>
        `).join('');
    }

    displayLabels(labels) {
        this.allLabels.innerHTML = labels.map(label => `
            <span class="inline-block bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm">
                ${label.name} (${label.confidence.toFixed(1)}%)
            </span>
        `).join('');
    }

    addToHistory(result) {
        this.analysisHistory.unshift(result);
        if (this.analysisHistory.length > 5) {
            this.analysisHistory.pop();
        }
        this.updateHistoryDisplay();
    }

    updateHistoryDisplay() {
        if (this.analysisHistory.length === 0) {
            this.historyList.innerHTML = '<p class="text-gray-500 text-center py-4">No hay análisis recientes</p>';
            return;
        }

        this.historyList.innerHTML = this.analysisHistory.map((item, index) => `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center space-x-3">
                    <div class="w-2 h-2 rounded-full ${
                        item.compliance.level === 'high' ? 'bg-green-500' :
                        item.compliance.level === 'medium' ? 'bg-yellow-500' : 'bg-red-500'
                    }"></div>
                    <div>
                        <p class="font-medium text-gray-800">${item.imageId}</p>
                        <p class="text-sm text-gray-500">${new Date(item.timestamp).toLocaleString()}</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="font-medium ${item.compliance.level === 'high' ? 'text-green-600' :
                                           item.compliance.level === 'medium' ? 'text-yellow-600' : 'text-red-600'}">
                        ${item.compliance.score}%
                    </p>
                    <p class="text-xs text-gray-500">${item.compliance.status}</p>
                </div>
            </div>
        `).join('');
    }

    showProgress(show) {
        if (show) {
            this.uploadProgress.classList.remove('hidden');
            this.analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Analizando...';
        } else {
            this.uploadProgress.classList.add('hidden');
            this.analyzeBtn.innerHTML = '<i class="fas fa-search mr-2"></i>Analizar Imagen';
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'error' ? 'bg-red-500 text-white' : 'bg-blue-500 text-white'
        }`;
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'} mr-2"></i>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SafetyDetectionApp();
});
