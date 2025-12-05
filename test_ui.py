"""
Script de prueba para demostrar el flujo completo de firma y verificación
"""

import requests
import json

API_BASE = "http://localhost:5000/api"

print("=" * 60)
print("PRUEBA COMPLETA DE LA WALLET UI")
print("=" * 60)

# Paso 1: Cargar la wallet
print("\n[1] Cargando wallet...")
load_response = requests.post(f"{API_BASE}/wallet/load", json={
    "keystorePath": "test_wallet.json",
    "passphrase": "test12345678"  # Usa tu passphrase real
})

if not load_response.ok:
    print(f"❌ Error al cargar wallet: {load_response.text}")
    exit(1)

load_data = load_response.json()
if not load_data['success']:
    print(f"❌ Error: {load_data.get('error')}")
    exit(1)

session_id = load_data['sessionId']
wallet = load_data['wallet']

print(f"✅ Wallet cargada exitosamente!")
print(f"   Dirección: {wallet['address']}")
print(f"   Llave Pública: {wallet['publicKey'][:32]}...")

# Paso 2: Firmar una transacción
print("\n[2] Firmando transacción...")
tx_data = {
    "from": wallet['address'],
    "to": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "value": "1000",
    "nonce": 0,
    "data_hex": ""
}

sign_response = requests.post(f"{API_BASE}/wallet/sign", json={
    "sessionId": session_id,
    "transaction": tx_data
})

if not sign_response.ok:
    print(f"❌ Error al firmar: {sign_response.text}")
    exit(1)

sign_data = sign_response.json()
if not sign_data['success']:
    print(f"❌ Error: {sign_data.get('error')}")
    exit(1)

signature = sign_data['signature']
signed_tx = sign_data['signedTransaction']

print(f"✅ Transacción firmada exitosamente!")
print(f"\n--- DATOS PARA VERIFICAR ---")
print(f"\n📋 MENSAJE ORIGINAL (Copiar esto en el campo 'Mensaje/Tx Original'):")
print(json.dumps(signed_tx['tx'], indent=2))
print(f"\n🔐 FIRMA (Copiar esto en el campo 'Firma'):")
print(signature)
print(f"\n🔑 LLAVE PÚBLICA:")
print(signed_tx['pubkey_b64'])
print(f"\n📍 DIRECCIÓN DEL REMITENTE:")
print(wallet['address'])

# Paso 3: Verificar la firma
print("\n[3] Verificando firma...")
verify_response = requests.post(f"{API_BASE}/signature/verify", json={
    "fromAddress": wallet['address'],
    "originalMessage": json.dumps(signed_tx['tx']),
    "signature": signature,
    "publicKey": signed_tx['pubkey_b64']
})

if not verify_response.ok:
    print(f"❌ Error al verificar: {verify_response.text}")
    exit(1)

verify_data = verify_response.json()
if not verify_data['success']:
    print(f"❌ Error: {verify_data.get('error')}")
    exit(1)

print(f"\n{'✅ FIRMA VÁLIDA!' if verify_data['valid'] else '❌ FIRMA INVÁLIDA'}")
print(f"   Razón: {verify_data['reason']}")
if verify_data.get('details'):
    print(f"   Detalles: {verify_data['details']}")

# Paso 4: Cerrar sesión
print("\n[4] Cerrando sesión...")
logout_response = requests.post(f"{API_BASE}/wallet/logout", json={
    "sessionId": session_id
})

print("\n" + "=" * 60)
print("✅ PRUEBA COMPLETADA")
print("=" * 60)
print("\nAhora puedes usar estos datos en la interfaz web:")
print("1. Ve a http://localhost:5000")
print("2. Carga la wallet (o ya la tienes cargada)")
print("3. Ve a 'Firmar' y firma una transacción")
print("4. Copia el MENSAJE ORIGINAL y la FIRMA")
print("5. Ve a 'Verificar' y pega los datos")
