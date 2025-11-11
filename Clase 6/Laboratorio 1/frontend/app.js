// ==================== CONFIGURACIÓN ====================
let API_ENDPOINT = '';

// Cargar configuración
async function loadConfig() {
    try {
        const response = await fetch('config.json');
        const config = await response.json();
        API_ENDPOINT = config.apiEndpoint.replace(/\/$/, '');
        console.log('✓ Configuración cargada:', API_ENDPOINT);
    } catch (error) {
        console.error('Error cargando config.json:', error);
        API_ENDPOINT = window.location.origin;
    }
}

// ==================== INICIALIZACIÓN ====================
document.addEventListener('DOMContentLoaded', async () => {
    await loadConfig();
    setupEventListeners();
    loadDocuments();
});

function setupEventListeners() {
    // Upload
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFileSelect(e.dataTransfer.files);
    });
    
    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files);
    });
    
    uploadBtn.addEventListener('click', handleUpload);
    
    // Chat
    document.getElementById('sendBtn').addEventListener('click', handleQuery);
    document.getElementById('queryInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleQuery();
    });
}

// ==================== UPLOAD ====================
let selectedFile = null;

function handleFileSelect(files) {
    if (files.length > 0) {
        selectedFile = files[0];
        document.getElementById('uploadBtn').disabled = false;
        showMessage('uploadMessage', 'info', `Archivo seleccionado: ${selectedFile.name}`);
    }
}

async function handleUpload() {
    if (!selectedFile) {
        showMessage('uploadMessage', 'error', 'Por favor selecciona un archivo');
        return;
    }
    
    const btn = document.getElementById('uploadBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Subiendo...';
    
    try {
        const reader = new FileReader();
        reader.onload = async (e) => {
            try {
                const response = await fetch(`${API_ENDPOINT}/upload`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        filename: selectedFile.name,
                        file_content: e.target.result,
                    }),
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showMessage('uploadMessage', 'success', data.message);
                    selectedFile = null;
                    document.getElementById('fileInput').value = '';
                    loadDocuments();
                } else {
                    showMessage('uploadMessage', 'error', data.error || 'Error al subir');
                }
            } catch (error) {
                showMessage('uploadMessage', 'error', `Error: ${error.message}`);
            } finally {
                btn.disabled = false;
                btn.innerHTML = 'Subir Documento';
            }
        };
        reader.readAsText(selectedFile);
    } catch (error) {
        showMessage('uploadMessage', 'error', `Error: ${error.message}`);
        btn.disabled = false;
        btn.innerHTML = 'Subir Documento';
    }
}

async function loadDocuments() {
    try {
        const response = await fetch(`${API_ENDPOINT}/documents`);
        const data = await response.json();
        
        const list = document.getElementById('documentsList');
        if (data.documents && data.documents.length > 0) {
            list.innerHTML = data.documents.map(doc => `
                <div class="document-item">
                    <div class="name">📄 ${doc.filename}</div>
                    <div class="status">ID: ${doc.document_id} | Estado: ${doc.status}</div>
                </div>
            `).join('');
        } else {
            list.innerHTML = '<p style="color: #999; text-align: center;">No hay documentos</p>';
        }
    } catch (error) {
        console.error('Error cargando documentos:', error);
    }
}

// ==================== QUERY / RAG ====================
async function handleQuery() {
    const input = document.getElementById('queryInput');
    const question = input.value.trim();
    
    if (!question) {
        showMessage('queryMessage', 'error', 'Por favor escribe una pregunta');
        return;
    }
    
    // Agregar mensaje del usuario al chat
    addMessageToChat('user', question);
    input.value = '';
    
    const btn = document.getElementById('sendBtn');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_ENDPOINT}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Agregar respuesta del asistente
            addMessageToChat('assistant', data.answer, data.sources);
        } else {
            addMessageToChat('assistant', `Error: ${data.error}`);
        }
    } catch (error) {
        addMessageToChat('assistant', `Error: ${error.message}`);
    } finally {
        btn.disabled = false;
    }
}

function addMessageToChat(role, content, sources = null) {
    const chatMessages = document.getElementById('chatMessages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-item ${role}`;
    
    let html = `<div class="message-bubble">${escapeHtml(content)}`;
    
    if (sources && sources.length > 0) {
        html += '<div class="message-sources"><strong>Fuentes:</strong>';
        sources.forEach(source => {
            html += `<br>• ${source.document_id} (${(source.score * 100).toFixed(0)}%)`;
        });
        html += '</div>';
    }
    
    html += '</div>';
    messageDiv.innerHTML = html;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== UTILIDADES ====================
function showMessage(elementId, type, text) {
    const element = document.getElementById(elementId);
    element.className = `message ${type}`;
    element.textContent = text;
    element.style.display = 'block';
    
    if (type !== 'error') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}
