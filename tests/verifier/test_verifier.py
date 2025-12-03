import base64
from pathlib import Path
import sys


Directorios = Path(__file__).resolve().parents[2]
if str(Directorios) not in sys.path:
    sys.path.insert(0, str(Directorios))
from verifier import (
    verificar_firma,
    NonceStore,
    address_from_public_key,
)

def tx_firmado(nonce: int = 0) -> dict:
    public_key_bytes = b"dummypub"
    signature_bytes = b"dummy_signature"
    public_key_b64 = base64.b64encode(public_key_bytes).decode("utf-8")
    signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")

    from_address = address_from_public_key(public_key_bytes)
    tx = {
        "from_address": from_address,
        "to": "0xDESTINO123",
        "value": "100",
        "nonce": str(nonce),
        "timestamp": 1234567890,
    }

    data = {
        "tx": tx,
        "sig_scheme": "ed25519",
        "signature_b64": signature_b64,
        "public_key_b64": public_key_b64,
    }
    return data

def test_valid_transaction_ok(tmp_path: Path):
    nonce_store = NonceStore(tmp_path / "nonce_store.json")
    data = tx_firmado(nonce=0)
    resultado = verificar_firma(data, nonce_store)
    assert resultado.valido is True
    assert resultado.razon == "ok"

def test_replay_nonce(tmp_path: Path):
    nonce_store = NonceStore(tmp_path / "nonces.json")
    data = tx_firmado(nonce=0)
    rec1 = verificar_firma(data, nonce_store)
    rec2 = verificar_firma(data, nonce_store)
    assert rec1.valido is True
    assert rec1.razon == "ok"

    assert rec2.valido is False
    assert rec2.razon == "stale_nonce"

def test_bad_format_missing_field():
    data = tx_firmado(nonce=0)
    del data["tx"]["from_address"]
    resultado = verificar_firma(data, nonce_store=None)
    assert resultado.valido is False
    assert resultado.razon == "Formato invalido"

def test_address_mismatch(tmp_path: Path):
    nonce_store = NonceStore(tmp_path / "nonces.json")
    data = tx_firmado(nonce=0)
    data["tx"]["from_address"] = "0x" + "deadbeef" * 5
    resultado = verificar_firma(data, nonce_store)
    assert resultado.valido is False
    assert resultado.razon == "Direccion invalida"

def test_bad_signature(tmp_path: Path):
    nonce_store = NonceStore(tmp_path / "nonces.json")
    data = tx_firmado(nonce=0)
    data["signature_b64"] = base64.b64encode(b"").decode("utf-8")
    resultado = verificar_firma(data, nonce_store)
    assert resultado.valido is False
    assert resultado.razon == "Firma invalida"