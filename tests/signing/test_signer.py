import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from app.signer import Signer
from app.transaction import Transaction

def test_estructura_firma():
    # Generar llave temporal para probar que la estructura del JSON final es correcta
    priv = ed25519.Ed25519PrivateKey.generate()
    signer = Signer(priv)
    
    tx = Transaction("Alice", "Bob", 50, 1)
    signed_tx = signer.sign_transaction(tx)
    
    # Verificar campos obligatorios 
    assert "tx" in signed_tx
    assert "sig_scheme" in signed_tx
    assert signed_tx["sig_scheme"] == "Ed25519"
    assert "signature_b64" in signed_tx
    assert "pubkey_b64" in signed_tx

def test_golden_vector_ed25519():
    """
    Este es el GOLDEN VECTOR.
    Usamos una llave privada fija (hardcoded) para asegurar que 
    la firma generada sea SIEMPRE la misma.
    """
    # 1. Llave Privada Fija (32 bytes de semilla)
    seed_bytes = b'\x00' * 32 
    priv_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed_bytes)
    
    # 2. Transacción Fija
    # Usamos timestamp fijo para que no cambie el hash
    tx = Transaction(
        sender="0xAlice",
        receiver="0xBob",
        value="1000",
        nonce="5",
        gas_limit="21000",
        data_hex="",
        timestamp="2025-01-01T00:00:00Z"
    )
    
    # 3. Firmar
    signer = Signer(priv_key)
    resultado = signer.sign_transaction(tx)
    firma_generada = resultado["signature_b64"]
    print(f"\n\n--- COPIA ESTA FIRMA: {firma_generada} ---\n")
    
    # Por ahora solo validamos longitud
    assert len(firma_generada) > 10

    
    # EL GOLDEN VECTOR FINAL:
    firma_esperada = "FjXfomBjPv/KEOu+/rsOqKsf7ldaKrCvw3r2zFN8jejPWkBX0G6og3CQ3afT5h1k8a2wbpFf6kgQorHOnzcmCg=="
    
    assert resultado["signature_b64"] == firma_esperada