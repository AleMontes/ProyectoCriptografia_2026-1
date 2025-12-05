"""
API Server para Crypto Cold Wallet
Conecta el frontend HTML/CSS/JS con el backend Python
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import base64
import os
from pathlib import Path
from datetime import datetime

# Importar módulos del proyecto
from almallave import (
    crear_keystore,
    cargar_keystore,
    derivar_direccion_keccak,
    a_base64
)
from app.signer import Signer
from app.transaction import Transaction
from verifier import verificar_firma, NonceStore, VerificaResultato

app = Flask(__name__, static_folder='.')
CORS(app)  # Permitir CORS para desarrollo

# Estado de la sesión (en producción usar sesiones seguras)
active_wallets = {}

# ==================== Rutas para servir el frontend ====================

@app.route('/')
def index():
    """Sirve la página principal"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Sirve archivos estáticos (CSS, JS)"""
    return send_from_directory('.', path)

# ==================== API Endpoints ====================

@app.route('/api/wallet/create', methods=['POST'])
def create_wallet():
    """
    Crea una nueva wallet
    Body: { keystorePath, passphrase, description }
    """
    try:
        data = request.json
        keystore_path = data.get('keystorePath')
        passphrase = data.get('passphrase')
        description = data.get('description', 'Wallet creada desde la interfaz web')

        if not keystore_path or not passphrase:
            return jsonify({
                'success': False,
                'error': 'keystorePath y passphrase son requeridos'
            }), 400

        # Validar longitud de passphrase
        if len(passphrase) < 8:
            return jsonify({
                'success': False,
                'error': 'La passphrase debe tener al menos 8 caracteres'
            }), 400

        # Crear el keystore
        keystore_data = crear_keystore(keystore_path, passphrase)

        # Extraer llave pública
        pub_bytes_b64 = keystore_data['pubkey_b64']
        pub_bytes = base64.b64decode(pub_bytes_b64)

        # Derivar dirección
        address = derivar_direccion_keccak(pub_bytes)

        # Cargar la wallet para obtener el objeto completo
        priv_key, pub_bytes, metadata = cargar_keystore(keystore_path, passphrase)

        # Guardar en sesión activa
        session_id = os.urandom(16).hex()
        active_wallets[session_id] = {
            'private_key': priv_key,
            'public_key': pub_bytes,
            'address': address,
            'keystore_path': keystore_path,
            'description': description
        }

        return jsonify({
            'success': True,
            'sessionId': session_id,
            'wallet': {
                'address': address,
                'publicKey': a_base64(pub_bytes),
                'description': description,
                'keystorePath': keystore_path
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/wallet/load', methods=['POST'])
def load_wallet():
    """
    Carga una wallet existente
    Body: { keystorePath, passphrase }
    """
    try:
        data = request.json
        keystore_path = data.get('keystorePath')
        passphrase = data.get('passphrase')

        if not keystore_path or not passphrase:
            return jsonify({
                'success': False,
                'error': 'keystorePath y passphrase son requeridos'
            }), 400

        # Verificar que el archivo existe
        if not os.path.exists(keystore_path):
            return jsonify({
                'success': False,
                'error': f'No existe el archivo: {keystore_path}'
            }), 404

        # Cargar el keystore
        priv_key, pub_bytes, metadata = cargar_keystore(keystore_path, passphrase)

        # Derivar dirección
        address = derivar_direccion_keccak(pub_bytes)

        # Obtener descripción del metadata (si existe)
        description = metadata.get('description', 'Wallet cargada')

        # Guardar en sesión activa
        session_id = os.urandom(16).hex()
        active_wallets[session_id] = {
            'private_key': priv_key,
            'public_key': pub_bytes,
            'address': address,
            'keystore_path': keystore_path,
            'description': description
        }

        return jsonify({
            'success': True,
            'sessionId': session_id,
            'wallet': {
                'address': address,
                'publicKey': a_base64(pub_bytes),
                'description': description,
                'keystorePath': keystore_path
            }
        })

    except ValueError as e:
        # Error de passphrase incorrecta o checksum
        return jsonify({
            'success': False,
            'error': 'Passphrase incorrecta o archivo corrupto'
        }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/wallet/sign', methods=['POST'])
def sign_transaction():
    """
    Firma una transacción
    Body: { sessionId, transaction: { from, to, value, nonce, data_hex } }
    """
    try:
        data = request.json
        session_id = data.get('sessionId')
        tx_data = data.get('transaction')

        if not session_id or session_id not in active_wallets:
            return jsonify({
                'success': False,
                'error': 'Sesión inválida o expirada. Debes cargar una wallet primero.'
            }), 401

        if not tx_data:
            return jsonify({
                'success': False,
                'error': 'Datos de transacción requeridos'
            }), 400

        wallet = active_wallets[session_id]

        # Crear objeto Transaction (ajustar a los parámetros de tu clase)
        transaction = Transaction(
            sender=tx_data.get('from'),
            receiver=tx_data.get('to'),
            value=tx_data.get('value'),
            nonce=int(tx_data.get('nonce', 0)),
            data_hex=tx_data.get('data_hex', ''),
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )

        # Crear Signer y firmar
        signer = Signer(wallet['private_key'])
        signed_data = signer.sign_transaction(transaction)

        return jsonify({
            'success': True,
            'signature': signed_data['signature_b64'],
            'signedTransaction': signed_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/signature/verify', methods=['POST'])
def verify_signature():
    """
    Verifica una firma
    Body: {
        fromAddress,
        originalMessage (JSON string del tx),
        signature (base64),
        publicKey (base64)
    }
    """
    try:
        data = request.json
        from_address = data.get('fromAddress')
        original_message_str = data.get('originalMessage')
        signature_b64 = data.get('signature')
        public_key_b64 = data.get('publicKey')

        if not all([from_address, original_message_str, signature_b64, public_key_b64]):
            return jsonify({
                'success': False,
                'error': 'Faltan campos requeridos'
            }), 400

        # Parsear el mensaje original (debe ser JSON)
        try:
            tx_dict = json.loads(original_message_str)
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'error': 'El mensaje original no es JSON válido'
            }), 400

        # Construir el objeto de verificación (según el formato esperado por verifier.py)
        # El verifier espera que el tx tenga estos campos: from_address, to, value, nonce, timestamp
        verification_data = {
            'tx': tx_dict,
            'sig_scheme': 'ed25519',  # Minúsculas según verifier.py línea 80
            'signature_b64': signature_b64,
            'public_key_b64': public_key_b64
        }

        # Verificar firma
        resultado = verificar_firma(verification_data, nonce_store=None)

        return jsonify({
            'success': True,
            'valid': resultado.valido,
            'reason': resultado.razon,
            'details': resultado.detalles
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/wallet/update-description', methods=['POST'])
def update_description():
    """
    Actualiza la descripción de la wallet
    Body: { sessionId, description }
    """
    try:
        data = request.json
        session_id = data.get('sessionId')
        description = data.get('description', '')

        if not session_id or session_id not in active_wallets:
            return jsonify({
                'success': False,
                'error': 'Sesión inválida'
            }), 401

        # Actualizar en memoria
        active_wallets[session_id]['description'] = description

        # TODO: Aquí podrías actualizar el archivo keystore si quieres persistir la descripción

        return jsonify({
            'success': True,
            'message': 'Descripción actualizada correctamente'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/wallet/logout', methods=['POST'])
def logout_wallet():
    """
    Cierra la sesión de una wallet
    Body: { sessionId }
    """
    try:
        data = request.json
        session_id = data.get('sessionId')

        if session_id and session_id in active_wallets:
            # Limpiar datos sensibles
            del active_wallets[session_id]

        return jsonify({
            'success': True,
            'message': 'Sesión cerrada correctamente'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500


# ==================== Main ====================

if __name__ == '__main__':
    print("=" * 60)
    print("Crypto Cold Wallet API Server")
    print("=" * 60)
    print("Frontend: http://localhost:5000")
    print("API Base: http://localhost:5000/api")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
