// Obtener URL del API Gateway desde el servidor
async function getApiEndpoint() {
    try {
        const response = await fetch('config.json');
        const config = await response.json();
        console.log('Config cargado:', config);
        return config.apiEndpoint;
    } catch (error) {
        console.error('Error cargando config.json:', error);
        return null;
    }
}

let CONFIG = {
    registerUrl: null,
    publishUrl: null,
    subscribersUrl: null,
    adminKey: null
};

// Inicializar configuración
async function initConfig() {
    const apiEndpoint = await getApiEndpoint();
    if (apiEndpoint && apiEndpoint.includes('execute-api')) {
        CONFIG.registerUrl = `${apiEndpoint}/register`;
        CONFIG.publishUrl = `${apiEndpoint}/publish`;
        CONFIG.subscribersUrl = `${apiEndpoint}/subscribers`;
        console.log('CONFIG inicializado:', CONFIG);
    } else {
        console.error('API Endpoint no válido:', apiEndpoint);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initConfig);
