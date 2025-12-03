// ==================== Estado Global de la Aplicación ====================
const AppState = {
    walletLoaded: false,
    currentAddress: null,
    publicKey: null,
    description: null,
    sessionId: null,
    apiBaseUrl: 'http://localhost:5000/api'
};

// ==================== Elementos del DOM ====================
const DOM = {
    // Navigation
    navTabs: document.getElementById('navTabs'),
    tabButtons: document.querySelectorAll('.tab-button'),
    logoutBtn: document.getElementById('logoutBtn'),

    // Views
    loginView: document.getElementById('loginView'),
    dashboardView: document.getElementById('dashboardView'),
    signView: document.getElementById('signView'),
    verifyView: document.getElementById('verifyView'),

    // Wallet Status
    walletStatus: document.getElementById('walletStatus'),

    // Login Forms
    createWalletForm: document.getElementById('createWalletForm'),
    loadWalletForm: document.getElementById('loadWalletForm'),
    loginMessage: document.getElementById('loginMessage'),

    // Dashboard Elements
    walletAddress: document.getElementById('walletAddress'),
    copyAddressBtn: document.getElementById('copyAddressBtn'),
    publicKeyToggle: document.getElementById('publicKeyToggle'),
    publicKeyContent: document.getElementById('publicKeyContent'),
    publicKeyBase64: document.getElementById('publicKeyBase64'),
    copyPublicKeyBtn: document.getElementById('copyPublicKeyBtn'),
    walletDescription: document.getElementById('walletDescription'),
    saveDescriptionBtn: document.getElementById('saveDescriptionBtn'),

    // Sign Form
    signMessageForm: document.getElementById('signMessageForm'),
    txFrom: document.getElementById('txFrom'),
    txTo: document.getElementById('txTo'),
    txValue: document.getElementById('txValue'),
    txNonce: document.getElementById('txNonce'),
    txDataHex: document.getElementById('txDataHex'),
    signatureResult: document.getElementById('signatureResult'),
    signatureOutput: document.getElementById('signatureOutput'),
    copySignatureBtn: document.getElementById('copySignatureBtn'),
    signMessage: document.getElementById('signMessage'),

    // Verify Form
    verifySignatureForm: document.getElementById('verifySignatureForm'),
    txFromAddress: document.getElementById('txFromAddress'),
    originalMessage: document.getElementById('originalMessage'),
    signatureToVerify: document.getElementById('signatureToVerify'),
    verificationResult: document.getElementById('verificationResult'),
    verificationIcon: document.getElementById('verificationIcon'),
    verificationTitle: document.getElementById('verificationTitle'),
    verificationMessage: document.getElementById('verificationMessage'),
    verifyMessage: document.getElementById('verifyMessage')
};

// ==================== Utilidades ====================

/**
 * Muestra un mensaje en el área especificada
 * @param {HTMLElement} messageElement - Elemento donde mostrar el mensaje
 * @param {string} message - Texto del mensaje
 * @param {string} type - Tipo: 'success', 'error', 'warning'
 */
function showMessage(messageElement, message, type = 'success') {
    messageElement.textContent = message;
    messageElement.className = `message-area ${type} show`;

    // Auto-ocultar después de 5 segundos
    setTimeout(() => {
        messageElement.classList.remove('show');
    }, 5000);
}

/**
 * Copia texto al portapapeles
 * @param {string} text - Texto a copiar
 * @returns {Promise<boolean>}
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        // Fallback para navegadores más antiguos
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return true;
        } catch (err) {
            document.body.removeChild(textArea);
            return false;
        }
    }
}

/**
 * Valida que todos los campos requeridos estén llenos
 * @param {HTMLFormElement} form - Formulario a validar
 * @returns {boolean}
 */
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = 'var(--error)';
            isValid = false;

            // Remover el resaltado después de 2 segundos
            setTimeout(() => {
                input.style.borderColor = '';
            }, 2000);
        }
    });

    return isValid;
}

/**
 * Cambia entre vistas de la aplicación
 * @param {string} viewName - Nombre de la vista a mostrar
 */
function switchView(viewName) {
    // Ocultar todas las vistas
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });

    // Mostrar la vista seleccionada
    const targetView = document.getElementById(`${viewName}View`);
    if (targetView) {
        targetView.classList.add('active');
    }

    // Actualizar tabs activos
    DOM.tabButtons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.view === viewName) {
            btn.classList.add('active');
        }
    });
}

/**
 * Actualiza el estado de la wallet en el header
 * @param {boolean} isConnected - Si la wallet está conectada
 */
function updateWalletStatus(isConnected) {
    if (isConnected) {
        DOM.walletStatus.classList.add('connected');
        DOM.walletStatus.querySelector('.status-text').textContent = 'Wallet conectada';
    } else {
        DOM.walletStatus.classList.remove('connected');
        DOM.walletStatus.querySelector('.status-text').textContent = 'No conectado';
    }
}

/**
 * Carga la información de la wallet en el dashboard
 * @param {Object} walletData - Datos de la wallet
 * @param {string} sessionId - ID de sesión del servidor
 */
function loadWalletData(walletData, sessionId) {
    // Actualizar estado global
    AppState.walletLoaded = true;
    AppState.currentAddress = walletData.address || '';
    AppState.publicKey = walletData.publicKey || '';
    AppState.description = walletData.description || '';
    AppState.sessionId = sessionId;

    // Actualizar UI
    DOM.walletAddress.value = AppState.currentAddress;
    DOM.publicKeyBase64.value = AppState.publicKey;
    DOM.walletDescription.value = AppState.description;
    DOM.txFrom.value = AppState.currentAddress;

    // Mostrar navegación y cambiar a dashboard
    DOM.navTabs.style.display = 'flex';
    updateWalletStatus(true);
    switchView('dashboard');
}

/**
 * Limpia el estado de la wallet (logout)
 */
async function clearWalletData() {
    // Llamar al API para cerrar sesión
    if (AppState.sessionId) {
        try {
            await fetch(`${AppState.apiBaseUrl}/wallet/logout`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sessionId: AppState.sessionId })
            });
        } catch (err) {
            console.error('Error al cerrar sesión:', err);
        }
    }

    AppState.walletLoaded = false;
    AppState.currentAddress = null;
    AppState.publicKey = null;
    AppState.description = null;
    AppState.sessionId = null;

    // Limpiar campos
    DOM.walletAddress.value = '';
    DOM.publicKeyBase64.value = '';
    DOM.walletDescription.value = '';
    DOM.txFrom.value = '';
    DOM.signatureOutput.value = '';
    DOM.signatureResult.style.display = 'none';
    DOM.verificationResult.style.display = 'none';

    // Limpiar formularios
    DOM.createWalletForm.reset();
    DOM.loadWalletForm.reset();

    // Ocultar navegación y volver a login
    DOM.navTabs.style.display = 'none';
    updateWalletStatus(false);
    switchView('login');
}

// ==================== Event Listeners - Navigation ====================

// Navegación entre tabs
DOM.tabButtons.forEach(button => {
    button.addEventListener('click', (e) => {
        if (e.target.closest('.logout-tab')) return; // El logout se maneja aparte

        const viewName = button.dataset.view;
        if (viewName) {
            switchView(viewName);
        }
    });
});

// Botón de logout
DOM.logoutBtn.addEventListener('click', () => {
    if (confirm('¿Estás seguro de que quieres cerrar la wallet?')) {
        clearWalletData();
        showMessage(DOM.loginMessage, 'Wallet cerrada correctamente', 'success');
    }
});

// ==================== Event Listeners - Login View ====================

// Formulario: Crear Wallet
DOM.createWalletForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!validateForm(DOM.createWalletForm)) {
        showMessage(DOM.loginMessage, 'Por favor completa todos los campos requeridos', 'error');
        return;
    }

    const keystorePath = document.getElementById('createKeystorePath').value.trim();
    const passphrase = document.getElementById('createPassphrase').value;
    const description = document.getElementById('createDescription').value.trim();

    // Validación básica
    if (passphrase.length < 8) {
        showMessage(DOM.loginMessage, 'La passphrase debe tener al menos 8 caracteres', 'error');
        return;
    }

    showMessage(DOM.loginMessage, 'Creando wallet...', 'warning');

    try {
        const response = await fetch(`${AppState.apiBaseUrl}/wallet/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                keystorePath,
                passphrase,
                description
            })
        });

        const result = await response.json();

        if (result.success) {
            loadWalletData(result.wallet, result.sessionId);
            showMessage(DOM.loginMessage, 'Wallet creada exitosamente', 'success');
        } else {
            showMessage(DOM.loginMessage, result.error || 'Error al crear la wallet', 'error');
        }
    } catch (error) {
        console.error('Error al crear wallet:', error);
        showMessage(DOM.loginMessage, 'Error de conexión con el servidor', 'error');
    }
});

// Formulario: Cargar Wallet
DOM.loadWalletForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!validateForm(DOM.loadWalletForm)) {
        showMessage(DOM.loginMessage, 'Por favor completa todos los campos requeridos', 'error');
        return;
    }

    const keystorePath = document.getElementById('loadKeystorePath').value.trim();
    const passphrase = document.getElementById('loadPassphrase').value;

    showMessage(DOM.loginMessage, 'Cargando wallet...', 'warning');

    try {
        const response = await fetch(`${AppState.apiBaseUrl}/wallet/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                keystorePath,
                passphrase
            })
        });

        const result = await response.json();

        if (result.success) {
            loadWalletData(result.wallet, result.sessionId);
            showMessage(DOM.loginMessage, 'Wallet cargada exitosamente', 'success');
        } else {
            showMessage(DOM.loginMessage, result.error || 'Error al cargar la wallet', 'error');
        }
    } catch (error) {
        console.error('Error al cargar wallet:', error);
        showMessage(DOM.loginMessage, 'Error de conexión con el servidor', 'error');
    }
});

// ==================== Event Listeners - Dashboard ====================

// Copiar dirección de wallet
DOM.copyAddressBtn.addEventListener('click', async () => {
    const address = DOM.walletAddress.value;
    if (address) {
        const success = await copyToClipboard(address);
        if (success) {
            const originalHTML = DOM.copyAddressBtn.innerHTML;
            DOM.copyAddressBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polyline points="20 6 9 17 4 12"></polyline></svg>';
            setTimeout(() => {
                DOM.copyAddressBtn.innerHTML = originalHTML;
            }, 2000);
        }
    }
});

// Toggle Public Key (Collapsible)
DOM.publicKeyToggle.addEventListener('click', () => {
    DOM.publicKeyToggle.classList.toggle('open');
    DOM.publicKeyContent.classList.toggle('open');
});

// Copiar llave pública
DOM.copyPublicKeyBtn.addEventListener('click', async () => {
    const publicKey = DOM.publicKeyBase64.value;
    if (publicKey) {
        const success = await copyToClipboard(publicKey);
        if (success) {
            DOM.copyPublicKeyBtn.textContent = '✓ Copiado';
            setTimeout(() => {
                DOM.copyPublicKeyBtn.textContent = 'Copiar';
            }, 2000);
        }
    }
});

// Guardar descripción
DOM.saveDescriptionBtn.addEventListener('click', async () => {
    const description = DOM.walletDescription.value.trim();

    if (!AppState.sessionId) {
        alert('No hay sesión activa');
        return;
    }

    try {
        const response = await fetch(`${AppState.apiBaseUrl}/wallet/update-description`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sessionId: AppState.sessionId,
                description
            })
        });

        const result = await response.json();

        if (result.success) {
            AppState.description = description;
            DOM.saveDescriptionBtn.textContent = '✓ Guardado';
            setTimeout(() => {
                DOM.saveDescriptionBtn.textContent = 'Guardar';
            }, 2000);
        } else {
            alert('Error al guardar: ' + result.error);
        }
    } catch (error) {
        console.error('Error al guardar descripción:', error);
        alert('Error de conexión con el servidor');
    }
});

// ==================== Event Listeners - Sign View ====================

// Formulario: Firmar Mensaje
DOM.signMessageForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!validateForm(DOM.signMessageForm)) {
        showMessage(DOM.signMessage, 'Por favor completa todos los campos requeridos', 'error');
        return;
    }

    if (!AppState.walletLoaded || !AppState.sessionId) {
        showMessage(DOM.signMessage, 'Debes cargar una wallet primero', 'error');
        return;
    }

    const transaction = {
        from: DOM.txFrom.value.trim(),
        to: DOM.txTo.value.trim(),
        value: DOM.txValue.value.trim(),
        nonce: parseInt(DOM.txNonce.value, 10),
        data_hex: DOM.txDataHex.value.trim() || undefined
    };

    // Validación del nonce
    if (isNaN(transaction.nonce) || transaction.nonce < 0) {
        showMessage(DOM.signMessage, 'El nonce debe ser un número entero válido', 'error');
        return;
    }

    showMessage(DOM.signMessage, 'Firmando mensaje...', 'warning');

    try {
        const response = await fetch(`${AppState.apiBaseUrl}/wallet/sign`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sessionId: AppState.sessionId,
                transaction
            })
        });

        const result = await response.json();

        if (result.success) {
            // Mostrar todos los datos necesarios para verificar la firma
            const originalTxJson = JSON.stringify(result.signedTransaction.tx, null, 2);

            DOM.signatureOutput.value = `=== FIRMA (Base64) ===\n${result.signature}\n\n` +
                `=== MENSAJE ORIGINAL (JSON) - Copiar para verificar ===\n${originalTxJson}\n\n` +
                `=== LLAVE PÚBLICA (Base64) ===\n${result.signedTransaction.pubkey_b64}`;

            DOM.signatureResult.style.display = 'block';
            showMessage(DOM.signMessage, 'Mensaje firmado exitosamente. Los datos están en el área de texto.', 'success');

            // Guardar la transacción completa por si el usuario la necesita
            console.log('Transacción firmada completa:', result.signedTransaction);
        } else {
            showMessage(DOM.signMessage, result.error || 'Error al firmar', 'error');
        }
    } catch (error) {
        console.error('Error al firmar mensaje:', error);
        showMessage(DOM.signMessage, 'Error de conexión con el servidor', 'error');
    }
});

// Copiar firma generada
DOM.copySignatureBtn.addEventListener('click', async () => {
    const signature = DOM.signatureOutput.value;
    if (signature) {
        const success = await copyToClipboard(signature);
        if (success) {
            DOM.copySignatureBtn.textContent = '✓ Copiado';
            setTimeout(() => {
                DOM.copySignatureBtn.textContent = 'Copiar Firma';
            }, 2000);
        }
    }
});

// ==================== Event Listeners - Verify View ====================

// Formulario: Verificar Firma
DOM.verifySignatureForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!validateForm(DOM.verifySignatureForm)) {
        showMessage(DOM.verifyMessage, 'Por favor completa todos los campos requeridos', 'error');
        return;
    }

    const fromAddress = DOM.txFromAddress.value.trim();
    const originalMessage = DOM.originalMessage.value.trim();
    const signature = DOM.signatureToVerify.value.trim();

    // Validación básica de JSON
    let txDict;
    try {
        txDict = JSON.parse(originalMessage);
    } catch (err) {
        showMessage(DOM.verifyMessage, 'El mensaje original debe ser JSON válido', 'error');
        return;
    }

    showMessage(DOM.verifyMessage, 'Verificando firma...', 'warning');

    try {
        // Necesitamos la llave pública para verificar
        // Si no la tenemos, pedimos al usuario que la proporcione
        let publicKey = AppState.publicKey; // Usar la de la wallet cargada si existe

        // Si no hay wallet cargada, necesitamos que el usuario proporcione la llave pública
        if (!publicKey) {
            // Podríamos agregar un campo adicional en el formulario, pero por ahora
            // intentaremos derivar la dirección desde la llave pública del metadata
            showMessage(DOM.verifyMessage, 'Necesitas proporcionar la llave pública', 'warning');
            // Por simplicidad, asumimos que el usuario tiene una wallet cargada o
            // la transacción firmada incluye la llave pública
            return;
        }

        const response = await fetch(`${AppState.apiBaseUrl}/signature/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                fromAddress,
                originalMessage,
                signature,
                publicKey
            })
        });

        const result = await response.json();

        if (result.success) {
            DOM.verificationResult.style.display = 'block';

            if (result.valid) {
                DOM.verificationIcon.className = 'status-icon valid';
                DOM.verificationTitle.textContent = 'Firma Válida ✓';
                DOM.verificationMessage.textContent = result.reason || 'Firma verificada correctamente';
                showMessage(DOM.verifyMessage, 'La firma es válida', 'success');
            } else {
                DOM.verificationIcon.className = 'status-icon invalid';
                DOM.verificationTitle.textContent = 'Firma Inválida ✗';
                DOM.verificationMessage.textContent = result.reason || 'La firma no coincide';
                showMessage(DOM.verifyMessage, 'La firma no es válida', 'error');
            }
        } else {
            showMessage(DOM.verifyMessage, result.error || 'Error al verificar', 'error');
        }
    } catch (error) {
        console.error('Error al verificar firma:', error);
        showMessage(DOM.verifyMessage, 'Error de conexión con el servidor', 'error');
    }
});

// ==================== Inicialización ====================

// Limpiar mensajes cuando el usuario empiece a escribir
document.querySelectorAll('input, textarea').forEach(input => {
    input.addEventListener('input', () => {
        input.style.borderColor = '';
    });
});

// Log de inicialización
console.log('Crypto Cold Wallet UI initialized');
console.log('Ready to connect to Python backend');
