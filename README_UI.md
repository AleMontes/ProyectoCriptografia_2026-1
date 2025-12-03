# 🔐 Crypto Cold Wallet - Interfaz Web

Interfaz de usuario moderna y responsiva para gestionar tu billetera fría de criptomonedas.

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias

Asegúrate de tener Python 3.8+ instalado, luego ejecuta:

```bash
pip install -r requirements.txt
```

### 2. Iniciar el Servidor

Ejecuta el servidor Flask:

```bash
python api_server.py
```

Verás un mensaje como:

```
============================================================
🚀 Crypto Cold Wallet API Server
============================================================
Frontend: http://localhost:5000
API Base: http://localhost:5000/api
============================================================
```

### 3. Abrir la Aplicación

Abre tu navegador y navega a:

```
http://localhost:5000
```

## 📁 Estructura de Archivos

```
ProyectoCriptografia_2026-1/
│
├── index.html          # Frontend principal
├── style.css           # Estilos de la interfaz
├── script.js           # Lógica del frontend
├── api_server.py       # Servidor API Flask (¡NUEVO!)
│
├── almallave.py        # Gestión de keystores y criptografía
├── gestor_wallet.py    # Gestor de wallets
├── verifier.py         # Verificador de firmas
├── app/
│   ├── signer.py       # Firmador de transacciones
│   ├── transaction.py  # Modelo de transacción
│   └── canonicalizer.py# Canonicalizador JSON
│
└── requirements.txt    # Dependencias Python
```

## 🎯 Funcionalidades

### 1. 🔑 Crear/Cargar Wallet

- **Crear nueva wallet**: Genera un keystore cifrado con una passphrase
- **Cargar wallet existente**: Carga un keystore previamente creado

**Ejemplo de ruta de keystore:**
```
./wallets/mi_wallet.json
```

### 2. 🏠 Panel de Wallet

Una vez cargada la wallet, puedes:

- Ver tu **dirección** (formato Ethereum: `0x...`)
- Copiar la dirección al portapapeles
- Ver tu **llave pública** en Base64 (sección colapsable)
- Editar y guardar una **descripción** personalizada

### 3. ✍️ Firmar Transacción

Firma transacciones con los siguientes campos:

- **From**: Dirección origen (auto-relleno)
- **To**: Dirección destino
- **Value**: Cantidad a enviar
- **Nonce**: Número de transacción (entero)
- **Data Hex**: Datos opcionales en hexadecimal

La firma resultante se muestra en Base64 y puede copiarse.

### 4. ✅ Verificar Firma

Verifica la autenticidad de una firma:

- **Dirección del remitente**: `0x...`
- **Mensaje original**: JSON canónico de la transacción
- **Firma**: En formato Base64

El sistema indica si la firma es **válida** o **inválida** con razones.

## 🔒 Seguridad

- Las passphrases deben tener mínimo **8 caracteres**
- Las llaves privadas se manejan en el servidor y **nunca** se envían al cliente
- El sistema usa **Ed25519** para firmas criptográficas
- Derivación de claves con **Argon2id** (KDF resistente a ataques)
- Cifrado con **AES-256-GCM**

## 🌐 API Endpoints

El servidor expone los siguientes endpoints:

### `POST /api/wallet/create`
Crea una nueva wallet
```json
{
  "keystorePath": "./wallets/test.json",
  "passphrase": "mi-passphrase-segura",
  "description": "Mi wallet personal"
}
```

### `POST /api/wallet/load`
Carga una wallet existente
```json
{
  "keystorePath": "./wallets/test.json",
  "passphrase": "mi-passphrase-segura"
}
```

### `POST /api/wallet/sign`
Firma una transacción
```json
{
  "sessionId": "abc123...",
  "transaction": {
    "from": "0x...",
    "to": "0x...",
    "value": "1000",
    "nonce": 0,
    "data_hex": "0x..."
  }
}
```

### `POST /api/signature/verify`
Verifica una firma
```json
{
  "fromAddress": "0x...",
  "originalMessage": "{...}",
  "signature": "base64...",
  "publicKey": "base64..."
}
```

### `POST /api/wallet/logout`
Cierra la sesión
```json
{
  "sessionId": "abc123..."
}
```

## 🎨 Características de la UI

- **Diseño moderno**: Paleta oscura con acentos vibrantes
- **Totalmente responsivo**: Funciona en desktop, tablet y móvil
- **Animaciones suaves**: Transiciones y efectos hover
- **Mensajes de feedback**: Notificaciones de éxito, error y advertencia
- **Copiar al portapapeles**: Botones para copiar direcciones y firmas
- **Validación de formularios**: Validación en tiempo real

## 🧪 Probar la Aplicación

1. **Crear una wallet de prueba:**
   - Ruta: `./test_wallet.json`
   - Passphrase: `test12345678` (mínimo 8 caracteres)

2. **Firmar una transacción de prueba:**
   - To: `0x1234567890abcdef1234567890abcdef12345678`
   - Value: `1000`
   - Nonce: `0`

3. **Verificar la firma** copiando el mensaje original y la firma generada.

## ⚠️ Notas Importantes

- Esta es una **wallet fría** (cold wallet), diseñada para uso offline
- Las llaves privadas se guardan cifradas en archivos JSON locales
- **NUNCA** compartas tu passphrase o archivo keystore
- Haz **backups** de tus archivos keystore en lugares seguros
- El servidor Flask está en modo **desarrollo** - para producción usar un servidor WSGI

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'flask'"
```bash
pip install flask flask-cors
```

### Error: "No module named 'app.transaction'"
Asegúrate de que el archivo `app/transaction.py` exista y tenga la clase `Transaction`.

### Error: "CORS policy blocked"
El servidor Flask ya tiene CORS habilitado. Si persiste, verifica que estés accediendo desde `http://localhost:5000`.

## 📝 To-Do

- [ ] Agregar soporte para múltiples esquemas de firma (secp256k1)
- [ ] Implementar persistencia de sesiones seguras
- [ ] Agregar exportación de transacciones firmadas
- [ ] Historial de transacciones
- [ ] Modo oscuro/claro (toggle)

## 👨‍💻 Desarrollo

Creado como proyecto educativo de criptografía aplicada.

**Tecnologías:**
- Frontend: HTML5, CSS3, JavaScript (Vanilla)
- Backend: Python + Flask
- Criptografía: Ed25519, Argon2id, AES-GCM, Keccak256
