# 🚀 Guía de Instalación - Crypto Cold Wallet

## Instalación Rápida (Windows)

### Opción 1: Script Automático (Recomendado)
```bash
start.bat
```

El script instalará automáticamente todas las dependencias y lanzará el servidor.

### Opción 2: Manual

1. **Instalar dependencias:**
```bash
py -m pip install flask flask-cors cryptography argon2-cffi pycryptodome pytest
```

2. **Iniciar el servidor:**
```bash
py api_server.py
```

3. **Abrir el navegador:**
```
http://localhost:5000
```

---

## Instalación en Linux/Mac

1. **Instalar dependencias:**
```bash
pip3 install flask flask-cors cryptography argon2-cffi pycryptodome pytest
```

2. **Iniciar el servidor:**
```bash
python3 api_server.py
```

O usar el script:
```bash
chmod +x start.sh
./start.sh
```

---

## ⚠️ Nota sobre pysha3

El proyecto originalmente usaba `pysha3`, pero tiene problemas de compilación en Windows porque requiere Visual Studio Build Tools.

**Solución implementada:** Se usa `pycryptodome` como alternativa, que no requiere compilación.

El archivo `sha3_compat.py` proporciona compatibilidad automática. Si tienes `pysha3` instalado, lo usará; si no, usará `pycryptodome`.

---

## 📦 Dependencias Requeridas

```
flask==3.0.0         # Servidor web
flask-cors==4.0.0    # CORS para API
cryptography         # Criptografía (Ed25519, AES-GCM)
argon2-cffi          # KDF para derivación de claves
pycryptodome         # Keccak256 (alternativa a pysha3)
pytest               # Testing (opcional)
```

---

## 🔧 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'flask'"
**Solución:**
```bash
py -m pip install flask flask-cors
```

### Error: "ModuleNotFoundError: No module named 'sha3'"
**Solución:**
```bash
py -m pip install pycryptodome
```

El módulo `sha3_compat.py` se encargará automáticamente de usar pycryptodome.

### Error: "Address already in use" (Puerto 5000 ocupado)
**Solución:**
Edita `api_server.py` y cambia el puerto:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Cambiar a 5001
```

También actualiza `script.js`:
```javascript
apiBaseUrl: 'http://localhost:5001/api'  // Cambiar a 5001
```

### Error: "Unable to find a compatible Visual Studio installation" (pysha3)
**Solución:**
No instales `pysha3`. Usa `pycryptodome` en su lugar (ya incluido en las instrucciones).

---

## ✅ Verificar Instalación

1. **Verificar Python:**
```bash
py --version
```
Deberías ver Python 3.8 o superior.

2. **Verificar dependencias:**
```bash
py -c "import flask, cryptography, argon2, Crypto; print('OK')"
```
Debería imprimir "OK".

3. **Probar el servidor:**
```bash
curl http://localhost:5000/
```
Debería devolver el HTML de la página.

---

## 🎯 Primer Uso

1. **Abre el navegador:** http://localhost:5000

2. **Crea una wallet de prueba:**
   - Ruta: `test_wallet.json`
   - Passphrase: `test12345678` (mínimo 8 caracteres)
   - Descripción: "Mi primera wallet"

3. **Prueba a firmar una transacción:**
   - To: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`
   - Value: `1000`
   - Nonce: `0`

¡Disfruta tu Crypto Cold Wallet! 🔐
