// ========================================
// CONFIGURACIÓN DE LAS LAMBDAS AWS
// ========================================
console.log('📚 ============================================');
console.log('📚 SISTEMA DE GESTIÓN DE NOTAS - INICIANDO');
console.log('📚 ============================================');

const CONFIG = {
    LAMBDA_WRITE_URL: 'https://2icc3yp7h5ubkzydx46apbumw40npxbi.lambda-url.eu-west-1.on.aws/',
    LAMBDA_READ_URL: 'https://h4s7xgl477lmqu6ko6nyqdx7yi0fywdf.lambda-url.eu-west-1.on.aws/'
};

console.log('⚙️ Configuración cargada:');
console.log('   📝 Lambda Write URL:', CONFIG.LAMBDA_WRITE_URL);
console.log('   📖 Lambda Read URL:', CONFIG.LAMBDA_READ_URL);
console.log('');

// ========================================
// ELEMENTOS DEL DOM
// ========================================
console.log('🔍 Buscando elementos del DOM...');

const form = document.getElementById('notaForm');
const nombreInput = document.getElementById('nombre');
const calificacionInput = document.getElementById('calificacion');
const notaInput = document.getElementById('nota');
const submitBtn = document.getElementById('submitBtn');
const messageDiv = document.getElementById('message');
const refreshBtn = document.getElementById('refreshBtn');
const limitSelect = document.getElementById('limitSelect');
const notasList = document.getElementById('notasList');
const loading = document.getElementById('loading');
const emptyState = document.getElementById('emptyState');
const writeLambdaStatus = document.getElementById('writeLambdaStatus');

console.log('✅ Elementos DOM encontrados correctamente');
console.log('');

// ========================================
// FUNCIONES AUXILIARES
// ========================================

/**
 * Muestra un mensaje en la interfaz
 */
function showMessage(text, type = 'success') {
    console.log(`💬 Mostrando mensaje en UI: [${type.toUpperCase()}] ${text}`);
    
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.classList.remove('hidden');
    
    console.log('   ✓ Mensaje visible en la interfaz');
    
    // Ocultar después de 5 segundos
    setTimeout(() => {
        console.log('   ⏰ Ocultando mensaje (timeout 5s alcanzado)');
        messageDiv.classList.add('hidden');
    }, 5000);
}

/**
 * Actualiza el estado visual del badge de Lambda Write
 */
function updateWriteLambdaStatus(status = 'ready', text = 'Listo') {
    console.log(`🔄 Actualizando estado Lambda Write: ${text}`);
    
    writeLambdaStatus.innerHTML = `
        <i data-lucide="radio"></i>
        <span>${text}</span>
    `;
    
    if (status === 'loading') {
        writeLambdaStatus.classList.add('loading');
    } else {
        writeLambdaStatus.classList.remove('loading');
    }
    
    // Re-renderizar iconos
    lucide.createIcons();
}

/**
 * Formatea una fecha Unix timestamp a formato legible
 */
function formatDate(timestamp) {
    console.log(`📅 Formateando timestamp: ${timestamp}`);
    const date = new Date(timestamp * 1000);
    const formatted = date.toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    console.log(`   ✓ Fecha formateada: ${formatted}`);
    return formatted;
}

/**
 * Obtiene las iniciales de un nombre para el avatar
 */
function getInitials(name) {
    console.log(`👤 Generando iniciales para: ${name}`);
    const parts = name.trim().split(' ');
    const initials = parts.length >= 2 
        ? parts[0][0] + parts[1][0]
        : parts[0].substring(0, 2);
    console.log(`   ✓ Iniciales: ${initials.toUpperCase()}`);
    return initials.toUpperCase();
}

/**
 * Genera un color único basado en el nombre (para los avatares)
 */
function getColorForName(name) {
    const colors = [
        'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
        'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
        'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
        'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
    ];
    
    const index = name.length % colors.length;
    return colors[index];
}

// ========================================
// FUNCIÓN: REGISTRAR NOTA (Lambda Write)
// ========================================

async function registrarNota(nombre, calificacion, nota) {
    console.log('');
    console.log('📝 ============================================');
    console.log('📝 INICIANDO REGISTRO DE NOTA');
    console.log('📝 ============================================');
    
    const payload = {
        name: nombre,
        grade: parseFloat(calificacion),
        note: nota
    };
    
    console.log('📦 Preparando payload para Lambda Write:');
    console.log('   Datos:', JSON.stringify(payload, null, 2));
    console.log('   - Nombre:', nombre);
    console.log('   - Calificación:', calificacion);
    console.log('   - Observación:', nota);
    console.log('');
    
    console.log('🚀 Enviando petición POST a Lambda Write...');
    console.log('   URL:', CONFIG.LAMBDA_WRITE_URL);
    console.log('   Method: POST');
    console.log('   Headers: Content-Type: application/json');
    console.log('');
    
    try {
        const startTime = performance.now();
        console.log('⏱️  Timestamp inicio:', new Date().toISOString());
        
        const response = await fetch(CONFIG.LAMBDA_WRITE_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        const endTime = performance.now();
        const duration = (endTime - startTime).toFixed(2);
        
        console.log('');
        console.log('📨 Respuesta recibida de Lambda Write:');
        console.log('   Status:', response.status, response.statusText);
        console.log('   Tiempo de respuesta:', duration, 'ms');
        console.log('   Headers:', Object.fromEntries(response.headers.entries()));
        
        if (!response.ok) {
            console.error('❌ Error HTTP:', response.status);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log('');
        console.log('✅ Datos parseados correctamente:');
        console.log('   Respuesta completa:', JSON.stringify(data, null, 2));
        console.log('   ID generado:', data.id);
        console.log('   Status:', data.status);
        console.log('');
        console.log('🎉 ¡NOTA REGISTRADA EXITOSAMENTE EN DYNAMODB!');
        console.log('📝 ============================================');
        console.log('');
        
        return data;
        
    } catch (error) {
        console.error('');
        console.error('❌ ============================================');
        console.error('❌ ERROR AL REGISTRAR NOTA');
        console.error('❌ ============================================');
        console.error('   Tipo de error:', error.name);
        console.error('   Mensaje:', error.message);
        console.error('   Stack trace:', error.stack);
        console.error('❌ ============================================');
        console.error('');
        throw error;
    }
}

// ========================================
// FUNCIÓN: CARGAR NOTAS (Lambda Read)
// ========================================

async function cargarNotas(limit = 20) {
    console.log('');
    console.log('📖 ============================================');
    console.log('📖 INICIANDO CARGA DE NOTAS');
    console.log('📖 ============================================');
    
    // Construir URL con query parameter
    const url = `${CONFIG.LAMBDA_READ_URL}?limit=${limit}`;
    
    console.log('📦 Preparando petición GET para Lambda Read:');
    console.log('   Límite de registros:', limit);
    console.log('   Query parameter: limit=' + limit);
    console.log('');
    
    console.log('🚀 Enviando petición GET a Lambda Read...');
    console.log('   URL completa:', url);
    console.log('   Method: GET');
    console.log('');
    
    try {
        const startTime = performance.now();
        console.log('⏱️  Timestamp inicio:', new Date().toISOString());
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const endTime = performance.now();
        const duration = (endTime - startTime).toFixed(2);
        
        console.log('');
        console.log('📨 Respuesta recibida de Lambda Read:');
        console.log('   Status:', response.status, response.statusText);
        console.log('   Tiempo de respuesta:', duration, 'ms');
        
        if (!response.ok) {
            console.error('❌ Error HTTP:', response.status);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log('');
        console.log('✅ Datos recibidos de DynamoDB:');
        console.log('   Cantidad de items:', data.count);
        console.log('   Items encontrados:', data.items.length);
        console.log('');
        
        if (data.items && data.items.length > 0) {
            console.log('📋 Detalle de items recibidos:');
            data.items.forEach((item, index) => {
                console.log(`   [${index + 1}] ID: ${item.id}`);
                console.log(`       Nombre: ${item.name}`);
                console.log(`       Nota: ${item.note}`);
                console.log(`       Fecha: ${formatDate(item.created_at)}`);
                console.log('');
            });
        } else {
            console.log('ℹ️  No hay items para mostrar');
        }
        
        console.log('🎉 ¡NOTAS CARGADAS EXITOSAMENTE!');
        console.log('📖 ============================================');
        console.log('');
        
        return data;
        
    } catch (error) {
        console.error('');
        console.error('❌ ============================================');
        console.error('❌ ERROR AL CARGAR NOTAS');
        console.error('❌ ============================================');
        console.error('   Tipo de error:', error.name);
        console.error('   Mensaje:', error.message);
        console.error('   Stack trace:', error.stack);
        console.error('❌ ============================================');
        console.error('');
        throw error;
    }
}

// ========================================
// FUNCIÓN: RENDERIZAR NOTAS EN LA UI
// ========================================

function renderNotas(items) {
    console.log('');
    console.log('🎨 ============================================');
    console.log('🎨 RENDERIZANDO NOTAS EN LA INTERFAZ');
    console.log('🎨 ============================================');
    console.log('   Cantidad de notas a renderizar:', items.length);
    console.log('');
    
    // Limpiar lista actual
    console.log('🧹 Limpiando lista actual...');
    notasList.innerHTML = '';
    
    if (items.length === 0) {
        console.log('ℹ️  Lista vacía, mostrando estado vacío');
        emptyState.classList.remove('hidden');
        console.log('🎨 ============================================');
        console.log('');
        return;
    }
    
    emptyState.classList.add('hidden');
    
    // Ordenar por fecha (más reciente primero)
    console.log('📊 Ordenando items por fecha (más reciente primero)...');
    const sortedItems = [...items].sort((a, b) => b.created_at - a.created_at);
    console.log('   ✓ Items ordenados');
    console.log('');
    
    // Renderizar cada nota
    console.log('🎨 Generando HTML para cada nota...');
    sortedItems.forEach((item, index) => {
        console.log(`   [${index + 1}] Renderizando nota de ${item.name}...`);
        
        const notaElement = document.createElement('div');
        notaElement.className = 'nota-item';
        
        const initials = getInitials(item.name);
        const color = getColorForName(item.name);
        const fecha = formatDate(item.created_at);
        
        // Determinar color de calificación
        const grade = item.grade || 0;
        let gradeClass = 'grade-fail';
        if (grade >= 9) gradeClass = 'grade-excellent';
        else if (grade >= 7) gradeClass = 'grade-good';
        else if (grade >= 5) gradeClass = 'grade-pass';
        
        notaElement.innerHTML = `
            <div class="nota-header">
                <div class="nota-avatar" style="background: ${color}">
                    ${initials}
                </div>
                <div class="nota-info">
                    <h3>${item.name}</h3>
                    <div class="nota-id">ID: ${item.id.substring(0, 8)}...</div>
                </div>
                <div class="nota-grade ${gradeClass}">
                    <i data-lucide="award"></i>
                    <span>${grade.toFixed(1)}</span>
                </div>
            </div>
            <div class="nota-content">
                <p class="nota-text">${item.note}</p>
            </div>
            <div class="nota-footer">
                <i data-lucide="clock"></i>
                <span>${fecha}</span>
            </div>
        `;
        
        notasList.appendChild(notaElement);
        console.log(`       ✓ Nota añadida al DOM`);
    });
    
    console.log('');
    console.log('🎨 Re-renderizando iconos de Lucide...');
    lucide.createIcons();
    console.log('   ✓ Iconos actualizados');
    console.log('');
    console.log('🎉 ¡RENDERIZADO COMPLETADO!');
    console.log('🎨 ============================================');
    console.log('');
}

// ========================================
// MANEJADORES DE EVENTOS
// ========================================

// Manejador del formulario de registro
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    console.log('');
    console.log('🎯 ============================================');
    console.log('🎯 EVENTO: Formulario enviado');
    console.log('🎯 ============================================');
    
    const nombre = nombreInput.value.trim();
    const calificacion = calificacionInput.value.trim();
    const nota = notaInput.value.trim();
    
    console.log('📝 Datos del formulario:');
    console.log('   Nombre:', nombre);
    console.log('   Calificación:', calificacion);
    console.log('   Observación:', nota);
    console.log('');
    
    if (!nombre || !calificacion || !nota) {
        console.warn('⚠️  Validación fallida: campos vacíos');
        showMessage('Por favor, completa todos los campos', 'error');
        return;
    }
    
    const calificacionNum = parseFloat(calificacion);
    if (isNaN(calificacionNum) || calificacionNum < 0 || calificacionNum > 10) {
        console.warn('⚠️  Validación fallida: calificación inválida');
        showMessage('La calificación debe ser un número entre 0 y 10', 'error');
        return;
    }
    
    console.log('✅ Validación OK, procediendo con el registro...');
    console.log('');
    
    // Deshabilitar formulario
    console.log('🔒 Deshabilitando formulario durante el envío...');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i data-lucide="loader"></i><span>Registrando...</span>';
    lucide.createIcons();
    updateWriteLambdaStatus('loading', 'Enviando...');
    
    try {
        // Registrar nota
        const result = await registrarNota(nombre, calificacion, nota);
        
        console.log('🎊 Registro completado, actualizando UI...');
        
        // Mostrar mensaje de éxito
        showMessage(`✅ Nota registrada exitosamente! ID: ${result.id.substring(0, 8)}...`, 'success');
        
        // Limpiar formulario
        console.log('🧹 Limpiando campos del formulario...');
        form.reset();
        nombreInput.focus();
        
        // Recargar lista de notas
        console.log('🔄 Recargando lista de notas automáticamente...');
        const limit = parseInt(limitSelect.value);
        const data = await cargarNotas(limit);
        renderNotas(data.items);
        
    } catch (error) {
        console.error('💥 Error capturado en el manejador del formulario');
        showMessage('❌ Error al registrar la nota. Ver consola para detalles.', 'error');
    } finally {
        // Rehabilitar formulario
        console.log('🔓 Rehabilitando formulario...');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i data-lucide="send"></i><span>Registrar Nota</span>';
        lucide.createIcons();
        updateWriteLambdaStatus('ready', 'Listo');
        console.log('🎯 ============================================');
        console.log('');
    }
});

// Manejador del botón de actualizar
refreshBtn.addEventListener('click', async () => {
    console.log('');
    console.log('🔄 ============================================');
    console.log('🔄 EVENTO: Botón Actualizar clickeado');
    console.log('🔄 ============================================');
    
    const limit = parseInt(limitSelect.value);
    console.log('   Límite seleccionado:', limit);
    console.log('');
    
    // Mostrar loading
    console.log('⏳ Mostrando indicador de carga...');
    loading.classList.remove('hidden');
    notasList.innerHTML = '';
    emptyState.classList.add('hidden');
    
    // Deshabilitar botón
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = '<i data-lucide="loader"></i><span>Cargando...</span>';
    lucide.createIcons();
    
    try {
        const data = await cargarNotas(limit);
        renderNotas(data.items);
    } catch (error) {
        console.error('💥 Error capturado en el manejador de actualizar');
        showMessage('❌ Error al cargar las notas. Ver consola para detalles.', 'error');
        emptyState.classList.remove('hidden');
    } finally {
        // Ocultar loading y rehabilitar botón
        console.log('⏳ Ocultando indicador de carga...');
        loading.classList.add('hidden');
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = '<i data-lucide="refresh-cw"></i><span>Actualizar</span>';
        lucide.createIcons();
        console.log('🔄 ============================================');
        console.log('');
    }
});

// Manejador del selector de límite
limitSelect.addEventListener('change', () => {
    console.log('');
    console.log('🔢 Límite de registros cambiado a:', limitSelect.value);
    console.log('   Disparando recarga automática...');
    console.log('');
    refreshBtn.click();
});

// ========================================
// INICIALIZACIÓN
// ========================================

console.log('🚀 ============================================');
console.log('🚀 INICIALIZANDO APLICACIÓN');
console.log('🚀 ============================================');
console.log('');

// Cargar notas al iniciar
window.addEventListener('DOMContentLoaded', () => {
    console.log('📱 Evento DOMContentLoaded disparado');
    console.log('   Cargando notas iniciales...');
    console.log('');
    
    refreshBtn.click();
    
    console.log('');
    console.log('✅ ============================================');
    console.log('✅ APLICACIÓN LISTA PARA USAR');
    console.log('✅ ============================================');
    console.log('');
    console.log('💡 TIPS PARA LA CLASE:');
    console.log('   1. Mantén abierta esta consola (F12) para ver todas las trazas');
    console.log('   2. Cada llamada a Lambda muestra el payload enviado y la respuesta');
    console.log('   3. Los tiempos de respuesta se miden en milisegundos');
    console.log('   4. Los errores se muestran claramente con el stack trace');
    console.log('');
    console.log('🎓 ¡Listo para la clase! 📚');
    console.log('');
});
