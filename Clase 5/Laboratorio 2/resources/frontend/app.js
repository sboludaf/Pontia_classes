let isAdminAuthenticated = false;

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
    if (form) {
        form.addEventListener('submit', handleRegister);
    }
});

async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const btn = e.target.querySelector('button');

    if (!name || !email) {
        showMessage('registerMessage', 'error', 'Por favor completa todos los campos');
        return;
    }

    if (!CONFIG.registerUrl) {
        showMessage('registerMessage', 'error', 'Configuración no cargada');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = 'Registrando...';

    try {
        const response = await fetch(CONFIG.registerUrl, {
            method: 'POST',
            mode: 'cors',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('registerMessage', 'success', data.message);
            document.getElementById('registerForm').reset();
        } else {
            showMessage('registerMessage', 'error', data.error || 'Error al registrar');
        }
    } catch (error) {
        showMessage('registerMessage', 'error', `Error: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Registrarse';
    }
}

async function verifyAdminKey() {
    const key = document.getElementById('adminKey').value.trim();
    if (!key) {
        showMessage('adminMessage', 'error', 'Ingresa la clave de admin');
        return;
    }

    CONFIG.adminKey = key;
    isAdminAuthenticated = true;
    document.getElementById('adminPanel').style.display = 'block';
    showMessage('adminMessage', 'success', '✓ Acceso de administrador activado');
}

async function loadSubscribers() {
    if (!isAdminAuthenticated || !CONFIG.adminKey) {
        showMessage('adminMessage', 'error', 'Por favor verifica tu clave de administrador primero');
        return;
    }

    if (!CONFIG.subscribersUrl) {
        showMessage('adminMessage', 'error', 'Configuración no cargada');
        return;
    }

    const url = `${CONFIG.subscribersUrl}?admin_key=${CONFIG.adminKey}`;
    const btn = event.target;
    btn.disabled = true;
    btn.innerHTML = 'Cargando...';

    try {
        const response = await fetch(url, {
            method: 'GET',
            mode: 'cors'
        });

        const data = await response.json();

        if (response.ok) {
            renderSubscribers(data.subscribers);
        } else {
            showMessage('adminMessage', 'error', data.error || 'Error al cargar');
        }
    } catch (error) {
        showMessage('adminMessage', 'error', `Error: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Actualizar Suscriptores';
    }
}

function renderSubscribers(subscribers) {
    const list = document.getElementById('subscribersList');

    if (subscribers.length === 0) {
        list.innerHTML = '<div style="padding: 20px; text-align: center; color: #999;">No hay suscriptores</div>';
        return;
    }

    list.innerHTML = subscribers.map(sub => `
        <div class="subscriber-item">
            <strong>${sub.name}</strong>
            <p>${sub.email}</p>
        </div>
    `).join('');
}

async function handlePublish() {
    if (!isAdminAuthenticated || !CONFIG.adminKey) {
        showMessage('adminMessage', 'error', 'Por favor verifica tu clave de administrador primero');
        return;
    }

    if (!CONFIG.publishUrl) {
        showMessage('adminMessage', 'error', 'Configuración no cargada');
        return;
    }

    const subject = document.getElementById('subject').value.trim();
    const message = document.getElementById('message').value.trim();
    const btn = event.target;

    if (!subject || !message) {
        showMessage('adminMessage', 'error', 'Por favor completa asunto y mensaje');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = 'Enviando...';

    try {
        const response = await fetch(CONFIG.publishUrl, {
            method: 'POST',
            mode: 'cors',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                subject,
                message,
                admin_key: CONFIG.adminKey
            })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('adminMessage', 'success', data.message);
            document.getElementById('subject').value = '';
            document.getElementById('message').value = '';
        } else {
            showMessage('adminMessage', 'error', data.error || 'Error al enviar');
        }
    } catch (error) {
        showMessage('adminMessage', 'error', `Error: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Enviar a Confirmados';
    }
}

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
