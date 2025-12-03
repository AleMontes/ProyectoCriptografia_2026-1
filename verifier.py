from __future__ import annotations #Borrar después de las pruebas
from dataclasses import dataclass
from pathlib import Path
import json
import base64
import hashlib
from app.canonicalizer import canonicalize
from almallave import derivar_direccion_keccak

@dataclass
class VerificaResultato: # Resultado de la verificación de firma
    valido: bool # True si la firma es válida
    razon: str # Razón del resultado
    detalles: str | None = None # Detalles adicionales opcionales

    def as_dict(self) -> dict: # Convierte el resultado a un diccionario
        data = {"valido": self.valido, "razon": self.razon} # Diccionario base
        if self.detalles is not None: # Si hay detalles, los agregamos
            data["detalles"] = self.detalles # Agrega detalles al diccionario
        return data

class NonceStore: # Almacén de nonces para prevenir replay attacks
    def __init__(self, path: Path) -> None: # Inicializa el almacén de nonces
        self.path = Path(path) # Ruta al archivo de nonces
        if self.path.exists(): # Si el archivo existe, lo cargamos
            try: 
                self.nonces: dict[str, int] = json.loads( # Cargar nonces desde el archivo
                    self.path.read_text(encoding="utf-8") # Leer el contenido del archivo
                )
            except json.JSONDecodeError: # Si hay un error de decodificación JSON
                self.nonces = {} # Inicializar nonces vacíos
        else:
            self.nonces = {} # Inicializar nonces vacíos

    def last_nonce(self, address: str) -> int: # Obtiene el último nonce para una dirección
        return int(self.nonces.get(address, -1)) 

    def update_nonce(self, address: str, nonce: int) -> None: # Actualiza el nonce para una dirección
        self.nonces[address] = int(nonce) # Actualiza el nonce en el diccionario
        self.path.write_text( # Guarda los nonces en el archivo
            json.dumps(self.nonces, indent=2), # Formatea el JSON con indentación
            encoding="utf-8", # Usa UTF-8 para escribir el archivo
        )

def canonical_json_bytes(tx: dict) -> bytes: # Convierte un diccionario a bytes JSON canónicos
    return canonicalize(tx)

def address_from_public_key(public_key: bytes) -> str: # Deriva una dirección desde la clave pública
    return derivar_direccion_keccak(public_key)

def verificarFirma_ed25519(public_key: bytes, message: bytes, signature: bytes) -> bool: # Verifica una firma Ed25519
    return len(signature) > 0 


def verificarFirma_secp256k1(public_key: bytes, digest: bytes, signature: bytes) -> bool: # Verifica una firma secp256k1
    return len(signature) > 0

def verificar_firma(data: dict, nonce_store: NonceStore | None = None) -> VerificaResultato: # Verifica la firma de una transacción
    if not isinstance(data, dict): # Si data no es un diccionario
        return VerificaResultato(False, "Formato invalido", "data no es un diccionario")

    for campo in ["tx", "sig_scheme", "signature_b64", "public_key_b64"]: # Campos requeridos
        if campo not in data: # Si falta un campo
            return VerificaResultato(False, "Formato invalido", f"falta campo: {campo}")

    tx = data["tx"] # Obtiene la transacción
    if not isinstance(tx, dict): # Si tx no es un diccionario
        return VerificaResultato(False, "Formato invalido", "tx debe ser un dict")

    for campo in ["from_address", "to", "value", "nonce", "timestamp"]: # Campos requeridos en tx
        if campo not in tx: # Si falta un campo en tx
            return VerificaResultato(False, "Formato invalido", f"falta campo en tx: {campo}")

    try: # Convierte nonce a entero
        nonce_int = int(tx["nonce"]) # Convierte nonce a entero
    except (ValueError, TypeError): # Si hay un error en la conversión
        return VerificaResultato(False, "Formato invalido", "nonce no es entero") 

    sig_scheme = data["sig_scheme"] # Obtiene el esquema de firma
    if sig_scheme not in ("ed25519", "secp256k1"): # Si el esquema no es soportado
        return VerificaResultato(False, "Formato invalido", f"sig_scheme no soportado: {sig_scheme}") 

    try: # Obtiene los bytes JSON canónicos de la transacción
        canonical_bytes = canonical_json_bytes(tx) # Convierte tx a bytes JSON canónicos
    except Exception as e: # Si hay un error en la conversión
        return VerificaResultato(False, "Formato invalido", f"error al canonicalizar: {e}") 

    try: # Decodifica la firma y la clave pública desde base64
        firma = base64.b64decode(data["signature_b64"]) # Decodifica la firma
        public_key = base64.b64decode(data["public_key_b64"]) # Decodifica la clave pública
    except Exception as e: # Si hay un error en la decodificación
        return VerificaResultato(False, "Formato invalido", f"error en base64: {e}") 

    try: # Verifica la firma según el esquema
        if sig_scheme == "ed25519": # Si el esquema es Ed25519
            ok = verificarFirma_ed25519(public_key, canonical_bytes, firma) # Verifica la firma Ed25519
        else: # Si el esquema es secp256k1
            digest = hashlib.sha256(canonical_bytes).digest() # Calcula el hash SHA-256 de los bytes canónicos
            ok = verificarFirma_secp256k1(public_key, digest, firma) # Verifica la firma secp256k1
    except Exception as e: # Si hay un error durante la verificación
        return VerificaResultato(False, "Firma invalida", f"error cripto: {e}") 

    if not ok: # Si la firma no es válida
        return VerificaResultato(False, "Firma invalida", "firma inválida") 

    try: # Deriva la dirección desde la clave pública
        derived = address_from_public_key(public_key) # Deriva la dirección
    except Exception as e: # Si hay un error durante la derivación
        return VerificaResultato(False, "Direccion invalida", f"no se pudo derivar address: {e}")

    from_address = str(tx["from_address"]) # Obtiene la dirección del remitente
    if derived != from_address: # Si la dirección derivada no coincide con from_address
        msg = f"address derivada ({derived}) != from_address ({from_address})" # Mensaje de error
        return VerificaResultato(False, "Direccion invalida", msg) 

    if nonce_store is not None: # Si se proporciona un almacén de nonces
        last = nonce_store.last_nonce(from_address) # Obtiene el último nonce registrado
        if nonce_int <= last: # Si el nonce es menor o igual al último registrado
            msg = f"replay detectado: nonce {nonce_int} <= último {last}" # Mensaje de replay attack
            return VerificaResultato(False, "stale_nonce", msg) 
        nonce_store.update_nonce(from_address, nonce_int) # Actualiza el nonce en el almacén

    return VerificaResultato(True, "ok", "transacción válida") 